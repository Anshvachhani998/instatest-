from pyrogram import Client, filters
import os
import subprocess
import logging

@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Hello! Bot is running successfully!")


@Client.on_message(filters.command("restart"))
async def git_pull(client, message):
      
    working_directory = "/home/ubuntu/InstaDL2"

    process = subprocess.Popen(
        "git pull https://github.com/Anshvachhani998/instatest-",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE

    )

    stdout, stderr = process.communicate()
    output = stdout.decode().strip()
    error = stderr.decode().strip()
    cwd = os.getcwd()
    logging.info("Raw Output (stdout): %s", output)
    logging.info("Raw Error (stderr): %s", error)

    if error and "Already up to date." not in output and "FETCH_HEAD" not in error:
        await message.reply_text(f"❌ Error occurred: {os.getcwd()}\n{error}")
        logging.info(f"get dic {cwd}")
        return

    if "Already up to date." in output:
        await message.reply_text("🚀 Repository is already up to date!")
        return
      
    if any(word in output.lower() for word in [
        "updating", "changed", "insert", "delete", "merge", "fast-forward",
        "files", "create mode", "rename", "pulling"
    ]):
        await message.reply_text(f"📦 Git Pull Output:\n```\n{output}\n```")
        await message.reply_text("🔄 Git Pull successful!\n♻ Restarting bot...")

        subprocess.Popen("bash /home/ubuntu/InstaDL2/start.sh", shell=True)
        os._exit(0)

    await message.reply_text(f"📦 Git Pull Output:\n```\n{output}\n```")
