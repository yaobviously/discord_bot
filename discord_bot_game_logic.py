# -*- coding: utf-8 -*-
"""
Created on Wed May 10 10:48:48 2023

@author: yaobv
"""

import os
import openai
import datetime
import discord
import asyncio
import random
import pickle

from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

openai.organization = os.environ.get('OPENAI_ORG')
openai.api_key = os.environ.get('OPENAI_KEY')

with open('theme_list.pickle', 'rb') as file:
    themes = pickle.load(file)

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
            max_tokens=250,
            messages=prompt,
            temperature=1.1)
    )

    returned_list = response.choices[0]
    
    return returned_list.to_dict()['message']['content']


@bot.command(name="game")
async def game(ctx, *, rounds: int):

    # Initialize dictionary to store player choices and scores
    
    player_choices = {}
    player_scores = {}
    
    # initializing a set of artificial players
    artificial_players = [f'AI_{n}' for n in range(35)]

    for round_num in range(rounds):
        
        theme = random.choice(themes)
        
        await ctx.send(f"This round's theme is {theme}")
        # Generate a new list for each round
        list_text = await generate_list(theme)

        for item in list_text.split("\n\n"):
            await ctx.send(item)

        # Wait for each player to make a selection
        await asyncio.sleep(15.0)

        messages = []

        async for message in ctx.channel.history(after=datetime.datetime.now() - datetime.timedelta(seconds=30)):
            messages.append(message)

        for message in messages:
            player = message.author

            if player.bot or message.author == ctx.author:
                continue

            if player not in player_choices:
                if round_num < 1:
                    player_choices[player] = []
                else:
                    player_choices[player].append(
                        [-1 for n in range(round_num)])

            if message.content.isdigit():
                player_choices[player].append(int(message.content))

        for ai in artificial_players:

            if ai not in player_choices:
                if round_num < 1:
                    player_choices[ai] = []
                else:
                    player_choices[ai].append([-1 for n in range(round_num)])

            this_time = random.choice([1, 2, 3, 4, 5])
            if random.randint(0, 99) < 60:
                ai_choice = this_time
            else:
                ai_choice = random.choice([1, 2, 3, 4, 5])

            player_choices[ai].append(ai_choice)

        # creating the dictionaries to hold the choices, the counts for each,
        # and the round score
        round_choice_dict = {player: 0 for player in player_choices.keys()}
        count_dict = {i: 0 for i in range(1, 6)}
        round_score_dict = {player: 0 for player in player_choices.keys()}

        # getting the round scores
        for player in player_choices.keys():
            round_choice = player_choices[player][round_num]
            round_choice_dict[player] = round_choice

        for player in round_choice_dict.keys():
            choice_ = round_choice_dict[player]
            count_dict[choice_] += 1

        for player in round_score_dict.keys():
            choice_ = round_choice_dict[player]
            score_ = count_dict[choice_]
            round_score_dict[player] = score_

        max_count = max([x for x in count_dict.values()])
        
        is_supermajority = (max_count / len(player_choices.keys())) > 0.66

        if is_supermajority:

            max_choice = sorted(count_dict.items(),
                                key=lambda x: x[1], reverse=True)[0][1]

            for player in round_score_dict.keys():
                print("reverse")
                if round_choice_dict[player] == max_choice:
                    round_score_dict[player] = 0

        for player in round_score_dict.keys():
            if player not in player_scores:
                player_scores[player] = round_score_dict[player]
            else:
                player_scores[player] += round_score_dict[player]


    # Print the final player choices
    await ctx.send("Game over! Here are the top 3 final scores:")
    top_3 = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    for player in top_3:
        await ctx.send(f"{player[0]} scored {player[1]}")

bot.run(os.environ.get('DISCORD_TOKEN'))