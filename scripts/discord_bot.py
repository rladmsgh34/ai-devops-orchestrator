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
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

client = ConductorBot()

@client.event
async def on_ready():
    logger.info(f"🤖 지휘자 Discord 봇 로그인 완료: {client.user}")

@client.tree.command(name="develop", description="지휘자에게 자율 개발 미션을 부여합니다.")
@app_commands.describe(title="이슈 제목", body="상세 구현 요구사항")
async def develop(interaction: discord.Interaction, title: str, body: str):
    """Discord /develop 명령어 처리"""
    await interaction.response.defer() # 시간이 걸릴 수 있으므로 '생각 중...' 상태로 전환

    # 1. 지휘자 API 호출
    payload = {
        "command": "develop",
        "issue_title": title,
        "issue_body": body,
        "discord_reply_url": interaction.followup.display_message().jump_url # 알림을 보낼 위치 (또는 웹훅 URL)
    }
    
    # 실제로는 interaction.followup을 통해 나중에 결과를 보낼 것이므로 
    # API 서버에 interaction의 정보를 전달할 수 있는 구조가 필요함.
    # 여기서는 간단하게 API 호출 결과만 먼저 응답.
    
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
            embed.set_footer(text="GitHub Actions를 통해 작업이 진행됩니다. 완료 시 알림이 전송됩니다.")
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
