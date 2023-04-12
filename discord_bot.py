# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 19:58:50 2023

@author: yaobv
"""

import os
import openai

import discord
from discord.ext import commands

openai.organization = os.environ["OPEN_AI_ORG"]
openai.api_key = os.environ["OPEN_AI_KEY"]

intents = discord.Intents().default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

async def generate_list(theme):

    prompt = [
        {"role": "system", "content": "You are a helpful assistant. You love creating lists with one especially surprising element"},
        {"role": "user", "content": f"I would like a list of 5 well known {theme}. Please only include one very short sentence at most about each."}

    ]

    response = (
        openai
        .ChatCompletion
        .create(
            model="gpt-3.5-turbo",
            max_tokens=100,
            messages=prompt,
            temperature=1.1)
    )

    returned_list = response.choices[0]

    return returned_list.to_dict()['message']['content'].replace('\n', ' ')


@bot.command(name="game")
async def game(ctx, *, theme: str):
    print("the game function was called", theme)
    list_text = await generate_list(theme)
    await ctx.send(list_text)

bot.run(os.environ["DISCORD_TOKEN"])