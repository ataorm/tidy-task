# Name: Arianne Taormina
# OSU Email: taormina@oregonstate.edu
# Course: CS361 - Software Engineering I
# Assignment 5: Main Program Implementation (Milestone 1)
# Due Date: Nov 3, 2025

# Description:  To do list app with add task, edit task, complete task, and view all tasks functionality.
#               Contains examples of all Inclusivity Heuristics.
#               Microservices not yet implemented.

from TidyTaskModules import *

# Display app title, description
print_welcome()

while True:
    # Import saved to do list, saved completed task list, or start blank list(s)
    user_list = import_list('userlist.pkl')
    completed_task_list = import_list('completed.pkl')

    # Display main prompt, validate response
    start_prompt = ("Enter any of these commands to continue...\n\n"
                    "Add:  'A' to ADD a new item\n"
                    "View: 'V' to VIEW and manage all items on your to do list\n"
                    "Help: 'H' to get HELP with the app\n"
                    "Quit: 'Q' to QUIT the app\n\n"
                    ">> ")
    valid_responses = ['A', 'V', 'H', 'Q']
    cover_page_response = get_input(start_prompt, valid_responses)

    # Add task
    if cover_page_response == 'A':
        add_task(user_list)
        view_tasks_menu(user_list, completed_task_list)

    # View all tasks -- with add task, edit task, complete task options within
    if cover_page_response == 'V':
        view_tasks_menu(user_list, completed_task_list)

    # Get help
    if cover_page_response == 'H':
        get_help()

    # Quit app
    if cover_page_response == 'Q':
        clear_screen()
        print("You have exited Tidy Task. Good luck with your tasks!")
        break
