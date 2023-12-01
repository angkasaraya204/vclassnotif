import sys

from bs4 import BeautifulSoup, Tag
from requests import session

baseurl = "https://v-class.gunadarma.ac.id/"


def login(user, pwd):
  authdata = {'action': 'login', 'username': user, 'password': pwd}
  with session() as ses:
    r = ses.post(baseurl + 'login/index.php', data=authdata)
    return ses, r


## get all course list , returns a dictionary || course_name:course_link
def getCourses(ses_tuple):
  ses, _ = ses_tuple  # Mendapatkan objek sesi dari tuple, respons tidak digunakan (_)
  r = ses.get(baseurl + 'my/')
  print(r.url)

  if (r.status_code == 200):
    soup = BeautifulSoup(r.text, 'html.parser')
    course_dict = {}

    all_course_items = soup.find_all('div', class_='card-body p-3')

    for course_item in all_course_items:
      course_box = course_item.find('li', class_='course-listitem')
      course_link = course_box.find('a', class_='coursename').get('href')
      course_title = course_box.find('span', class_='categoryname').find('a')
      course_dict[course_title] = course_link
    return course_dict


## given a course link , returns the forum link
def get_forum_link(course_link, ses):
  r = ses.get(course_link)
  #     print(r.url)
  if (r.status_code == 200):
    soup = BeautifulSoup(r.text, 'html.parser')
    link = soup.find('div', class_='activityinstance').find('a').get('href')
    return link


## Forum Post Class
class Forum_Post:

  def __init__(self, link, title, author):
    self.link = link
    self.title = title
    self.author = author

  def __str__(self):
    post = "Link : " + self.link + "\n"
    post += "Title : " + self.title + "\n"
    post += "Author : " + self.author + "\n"
    return post


## given forum link , returns all the posts in the forum in a list
def get_forum_posts(forum_link, ses):
  r = ses.get(forum_link)

  if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    tbody = soup.find('tbody')

    if tbody is None:
      return []

    all_posts_ = tbody.find_all('tr', class_='discussion')
    post_ara = []

    for post in all_posts_:
      row = post.find('th', class_='topic').find('a')
      if row is not None:
        p_link = row.get('href')
        p_title = row.contents[0]
        p_author = post.find('td', class_='author').contents[0]
        post_ara.append(Forum_Post(p_link, p_title, p_author))
      else:
        pass


#             print(row)
#             print(p_title)
#             print(p_link)
#             print(p_author)
    return post_ara
'''
only one time use
writes the old posts to a separate file
'''

# def write_old_forum_posts(course_dict, session):
#   for c_name, c_link in course_dict.items():
#     forum_link = get_forum_link(c_link, session)
#     #     print(forum_link)
#     post_ara = get_forum_posts(forum_link, session)
#     with open(c_name + '_forum_old.txt', 'w') as file:

#       if (len(post_ara) == 0):
#         continue

#       for p in post_ara:
#         print(p)
#         file.write(p.link + "\n")
#     print('\n')
'''
from the files stored
returns a dictionary containing old forum links
'''


def get_old_forum_links(
    course_dict
):  ## returns a dictionary containing old forum links || c_name : old_forum_link_ara
  old_forum_links = {}
  for c_name, _ in course_dict.items():
    with open(c_name + '_forum_old.txt') as f:
      links = f.readlines()
    links = [x.strip() for x in links]
    old_forum_links[c_name] = links
  return old_forum_links


## returns a dictionary of only the new forum posts || c_name:forum_post_ara
def get_new_forum_posts(course_dict, old_forum_links, session):
  new_forum_posts = {}
  for c_name, c_link in course_dict.items():
    forum_link = get_forum_link(c_link, session)
    post_ara = get_forum_posts(forum_link, session)

    new_post_ara = []

    with open(c_name + '_forum_old.txt', 'a') as file:
      # Check if post_ara is None before using len
      if post_ara is None:
        continue

      if len(post_ara) == 0:
        continue

      for p in post_ara:
        if p.link not in old_forum_links[c_name]:
          # print(p)
          new_post_ara.append(p)
          file.write(p.link + "\n")

    new_forum_posts[c_name] = new_post_ara
  return new_forum_posts


'''
ACTIVITY
'''


## Course Activity
class Course_Activity:

  def __init__(self, link, title):
    self.link = link
    self.title = title

  def __str__(self):
    activity = "Link : " + self.link + "\n"
    activity += "Title : " + self.title + "\n"
    return activity


## given course link , returns all the activities in the forum in a list
def get_course_activities(course_link, ses):
  r = ses.get(course_link)

  if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    temp = soup.find('div', class_='course-content')

    # Print or log the type of temp
    print("Type of temp:", type(temp))

    # Check if temp is a Tag before using find_all
    if temp and isinstance(temp, Tag):
      all_links = temp.find_all('div', class_='activityinstance')

      activity_ara = []

      for link_container in all_links:
        link = link_container.find('a').get('href')
        title = link_container.find('span', class_='instancename').contents[0]
        activity_ara.append(Course_Activity(link, title))

      return activity_ara
    else:
      print("Error: 'temp' is not a Tag or is None")


'''
only one time use
writes the old posts to a separate file
'''

# def write_old_activities(course_dict, session):
#   for c_name, c_link in course_dict.items():
#     activity_ara = get_course_activities(c_link, session)
#     with open(c_name + '_activity_old.txt', 'w') as file:

#       if (len(activity_ara) == 0):
#         continue

#       for p in activity_ara:
#         file.write(p.link + "\n")
# print('\n')
'''
from the files stored
returns a dictionary containing old activity links
'''


def get_old_activity_links(
    course_dict
):  ## returns a dictionary containing old forum links || c_name : old_forum_link_ara
  old_activity_links = {}
  for c_name, _ in course_dict.items():
    with open(c_name + '_activity_old.txt') as f:
      links = f.readlines()
    links = [x.strip() for x in links]
    old_activity_links[c_name] = links
  return old_activity_links


## returns a dictionary of only the new activity posts || c_name:activity_post_ara
def get_new_activity_posts(course_dict, old_activity_links, session):
  new_activity_posts = {}
  for c_name, c_link in course_dict.items():
    activity_ara = get_course_activities(c_link, session)

    new_post_ara = []

    with open(c_name + '_activity_old.txt', 'a') as file:
      if activity_ara is None:
        continue

      if (len(activity_ara) == 0):
        continue

      for p in activity_ara:
        if p.link not in old_activity_links[c_name]:
          # print(p)
          new_post_ara.append(p)
          file.write(p.link + "\n")

    new_activity_posts[c_name] = new_post_ara
  return new_activity_posts