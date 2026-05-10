import discord
from discord import app_commands
import requests
import os
import asyncio
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord_bot")

# 설정 (환경 변수 또는 직접 입력)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("CONDUCTOR_API_URL", "http://localhost:8000")
GUILD_ID = os.getenv("DISCORD_GUILD_ID") # 특정 서버에서만 작동하게 하려면 설정

class ConductorBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        try:
            if GUILD_ID:
                guild = discord.Object(id=int(GUILD_ID))
                # 1. 기존 명령어 초기화 (충돌 방지)
                self.tree.clear_commands(guild=guild)
                self.tree.copy_global_to(guild=guild)
                logger.info(f"🔄 서버(ID: {GUILD_ID}) 명령 리스트 초기화 및 재등록 중...")
                await self.tree.sync(guild=guild)
            else:
                self.tree.clear_commands(guild=None)
                logger.info("🔄 글로벌 명령 리스트 초기화 및 재등록 중...")
                await self.tree.sync()
            logger.info("✅ 명령 동기화 완료! (/develop, /setup, /status 사용 가능)")
        except discord.errors.Forbidden as e:
            logger.error(f"❌ 권한 부족으로 명령을 동기화할 수 없습니다: {e}")
            logger.error("💡 봇 초대 시 'applications.commands' 스코프를 포함했는지 확인하세요.")
        except Exception as e:
            logger.error(f"❌ 동기화 중 오류 발생: {e}")

client = ConductorBot()

@client.event
async def on_ready():
    logger.info(f"🤖 지휘자 Discord 봇 로그인 완료: {client.user}")
    
    # 채널 자동 관리 로직
    if GUILD_ID:
        guild = client.get_guild(int(GUILD_ID))
        if guild:
            await setup_conductor_channels(guild)

async def setup_conductor_channels(guild):
    """지휘자 운영을 위한 채널 및 웹훅 자동 설정"""
    required_channels = {
        "지휘-통제실": "자율 개발 명령(/develop)을 내리는 곳입니다.",
        "결과-보고": "지휘자의 작업 결과(PR 생성 등)가 보고되는 곳입니다.",
        "사고-기록": "과거 사고 사례 및 분석 로그가 기록되는 곳입니다."
    }
    
    existing_channels = {c.name: c for c in guild.text_channels}
    
    for name, desc in required_channels.items():
        if name not in existing_channels:
            logger.info(f"🔨 채널 생성 중: #{name}")
            category = discord.utils.get(guild.categories, name="CONDUCTOR")
            if not category:
                category = await guild.create_category("CONDUCTOR")
            
            new_channel = await guild.create_text_channel(name, topic=desc, category=category)
            existing_channels[name] = new_channel
            
    # 결과-보고 채널에 웹훅 자동 생성
    report_channel = existing_channels["결과-보고"]
    webhooks = await report_channel.webhooks()
    if not webhooks:
        webhook = await report_channel.create_webhook(name="Conductor Reporting Webhook")
        logger.info(f"✅ 웹훅 생성 완료! GitHub Secrets (DISCORD_WEBHOOK)에 등록하세요: {webhook.url}")
        # 이 정보를 관리자에게 DM으로 보내거나 콘솔에 출력
        print(f"\n{'='*60}\n[ACTION REQUIRED] GitHub Secrets (DISCORD_WEBHOOK) 에 다음 URL을 등록하세요:\n{webhook.url}\n{'='*60}\n")
    else:
        logger.info(f"ℹ️ 기존 웹훅 사용 가능: {webhooks[0].url}")

@client.tree.command(name="setup", description="지휘자 전용 채널 및 환경을 자동으로 구축합니다.")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    """수동으로 환경 구축 실행"""
    await interaction.response.send_message("🛠️ 지휘자 환경을 구축 중입니다...")
    await setup_conductor_channels(interaction.guild)
    await interaction.edit_original_response(content="✅ 지휘자 환경(채널 및 웹훅) 구축이 완료되었습니다!")

@client.tree.command(name="develop", description="지휘자에게 자율 개발 미션을 부여합니다.")
@app_commands.describe(title="이슈 제목", body="상세 구현 요구사항")
async def develop(interaction: discord.Interaction, title: str, body: str):
    """Discord /develop 명령어 처리"""
    await develop_logic(interaction, title, body)

@client.tree.command(name="new", description="[Alias] 지휘자에게 자율 개발 미션을 부여합니다.")
@app_commands.describe(title="이슈 제목", body="상세 구현 요구사항")
async def new_alias(interaction: discord.Interaction, title: str, body: str):
    """Discord /new 명령어 처리 (하위 호환성용)"""
    await develop_logic(interaction, title, body)

async def develop_logic(interaction: discord.Interaction, title: str, body: str):
    await interaction.response.defer()
    
    payload = {
        "command": "develop",
        "issue_title": title,
        "issue_body": body,
        "discord_reply_url": interaction.followup.display_message().jump_url if interaction.followup.display_message() else None
    }
    
    try:
        response = requests.post(f"{API_URL}/agent/trigger", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            embed = discord.Embed(
                title="🚀 자율 개발 워크플로 시작",
                description=f"**제목:** {title}\n**상태:** {result.get('message')}",
                color=discord.Color.blue()
            )
            embed.add_field(name="과거 사례 주입", value="✅ 완료" if result.get("context_injected") == "success" else "➖ 없음")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ API 오류: {response.status_code}")
    except Exception as e:
        logger.error(f"API 호출 실패: {e}")
        await interaction.followup.send(f"❌ 지휘자 API 서버에 연결할 수 없습니다: {e}")

@client.tree.command(name="status", description="현재 진행 중인 지휘자 작업의 상태를 확인합니다.")
async def status(interaction: discord.Interaction):
    """현재 상태 조회 (Placeholder)"""
    await interaction.response.send_message("🔍 현재 모든 시스템 정상 작동 중. 실행 중인 자율 개발 작업은 GitHub Actions 탭을 확인하세요.")

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
    else:
        client.run(TOKEN)
