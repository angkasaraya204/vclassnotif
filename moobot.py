import sys
import os

import asyncio

from moodle_scrapper import (get_new_activity_posts, get_new_forum_posts,
                             get_old_activity_links, get_old_forum_links,
                             getCourses, login)

from datetime import datetime

import discord

STUDENT_ID = "angkasaraya@student.gunadarma.ac.id"
LOGIN_PASSWORD = "anakpertama01"
CHANNEL_ID = 1180050844423569460  # don't use double quote


class MyClient(discord.Client):

  def __init__(self, *args, **kwargs):
    my_intents = discord.Intents.default()
    super().__init__(*args, **kwargs, intents=my_intents)

  async def on_ready(self):
    if self.user is not None:
      print('Logged in as')
      print(self.user.name)
      print(self.user.id)
      print('------')
      await self.my_background_task()
    else:
      print(
          'User is not defined. Make sure to initialize self.user correctly.')

  async def on_connect(self):
    self.bg_task = self.loop.create_task(self.my_background_task())

  async def my_background_task(self):
    await self.wait_until_ready()
    channel = self.get_channel(CHANNEL_ID)  # channel ID goes here
    count = 0

    while not self.is_closed():

      count += 1
      print("Count :", count)

      # dd/mm/YY H:M:S
      now = datetime.now()
      dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
      print("date and time =", dt_string)
      '''
          FORUMS
          '''
      print("getiing Old Forum Links ... \n")
      old_forum_links = get_old_forum_links(course_dict)
      # print(old_forum_links)

      print("getiing New Forum Posts ... \n")
      new_forum_posts = get_new_forum_posts(course_dict, old_forum_links,
                                            session)
      # print(new_forum_posts)
      '''
          ACTIVITY
          '''
      print("getiing Old Activity Links ... \n")
      old_activity_links = get_old_activity_links(course_dict)
      # print(old_forum_links)

      print("getiing New Activity Posts ... \n")
      new_activity_posts = get_new_activity_posts(course_dict,
                                                  old_activity_links, session)
      # print(new_activity_posts)

      ## for testing only
      for c_name, post_ara in new_forum_posts.items():

        if (len(post_ara) == 0):
          continue

        for p in post_ara:
          print(p)

          # DISCORD CHANNEL NOTIFICATION
          if channel is not None:
            embedVar = discord.Embed(title="Forum Post ( " + c_name +
                                     " ) :rotating_light: ",
                                     description=p.title,
                                     color=0xb331bd)
            embedVar.add_field(name="Link :paperclips: ",
                               value=p.link,
                               inline=False)
            embedVar.add_field(name="Teacher :person_fencing: ",
                               value="`" + p.author + "`",
                               inline=False)
            try:
              await channel.send(embed=embedVar)
              await asyncio.sleep(30)  ## 30 seconds
            except Exception as e:
              print(f"Failed to send message: {e}")
          else:
            print("Channel is None. Check if the channel is valid or exists.")

      for c_name, post_ara in new_activity_posts.items():

        if (len(post_ara) == 0):
          continue

        for p in post_ara:
          print(p)
          # DISCORD CHANNEL NOTIFICATION
          embedVar = discord.Embed(title="New Activity ( " + c_name +
                                   " ) :boom: ",
                                   description=p.title,
                                   color=0xfc9803)
          embedVar.add_field(name="Link :paperclips: ",
                             value=p.link,
                             inline=False)
          await channel.send(embed=embedVar)
          await asyncio.sleep(30)  ## 30 seconds

      await asyncio.sleep(20 * 60)  ## check after 20 minutes


def setup(client):
  client.add_cog(MyClient(client))


if __name__ == "__main__":

  #logging in
  print("logging in...\n")
  session = login(STUDENT_ID, LOGIN_PASSWORD)

  #get courses
  print("getting Courses...\n")
  course_dict = getCourses(session)
  print(course_dict)

  print("GET FORUM AND ACTIVITIES UPDATED")

  client = MyClient()
  token = os.getenv('TOKEN')

  if token is not None:
    client.run(token)
  else:
    print("Error: Token is not available.")