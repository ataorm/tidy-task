# Name: Arianne Taormina
# OSU Email: taormina@oregonstate.edu
# Course: CS361 - Software Engineering I
# Assignment 5: Main Program Implementation (Milestone 1)
# Due Date: Nov 3, 2025

# Description:  Modules for Main Program implementation.


# TODO: Add functionality to recover task from completed.pkl
#   Update: add status to regular object incomplete/complete
#   Update: 2nd list should be for DELETE + recovery from delete
# TODO: Add delete functionality (does not get added to completed.pkl)
# TODO: Choice: (main) use default file, start new, or enter own file name


import pickle, time, textwrap


def print_welcome():
    """
    Print title and welcome message for Tidy Task app.

    :param:     none

    :return:    none
    """
    print("\nT I D Y   T A S K\n")
    print("The simple app for tracking the tasks on your to do list.\n"
          "Add, view, edit, and complete tasks on your to do list.")
    print("_" * 58, "\n")


def import_list(filename):
    """
    Returns existing saved list, or blank list if none found.
    Requires pickle module.

    :param filename:    filepath of saved list

    :return:            user_list (dictionary)
    """
    # Find saved list
    try:
        with open(filename, 'rb') as readfile:
            user_list = pickle.load(readfile)
    # If no saved list found, create blank list
    except FileNotFoundError:
        with open(filename, 'wb') as outputfile:
            if filename == 'userlist.pkl':
                print("No saved to do list found. New list has been created.\n")
            user_list = {}
    # If file found but blank, create blank list
    except EOFError:
        user_list = {}

    # Return list
    return user_list


def get_input(prompt, valid_responses):
    """
    Get user input for navigation prompts in app, validate response,
    and return input response.

    :param prompt:              prompt string
    :param valid_responses:     list of valid responses for input validation

    :return:                    user input response to prompt (str)
    """
    # Main prompt
    user_response = input(prompt).upper()

    # Validate input
    while user_response not in str(valid_responses):
        user_response = input(prompt).upper()

    # Return response
    return user_response

    # TODO: Fix taskid validation


def clear_screen():
    """
    Simulates clearing of CLI.

    :param:     none

    :return:    none
    """
    print('\n' * 100)


def print_progress_bar(step_list, step_num):
    """
    Display progress bar for steps in process, with emphasis on current step.
    Returns next step number to print next progress bar with correct emphasis.

    :param step_list:   List of steps in process
    :param step_num:    Number of current step in list

    :return:            step_num (inc +1)
    """
    clear_screen()
    for i in range(len(step_list)):
        width = len(str(step_list[i]))
        # Print step without emphasis if not current step
        if i != step_num:
            print(f"{step_list[i]}".center(width + 4), end="")
        # Print step with emphasis if current step
        else:
            print(f"[ {step_list[i]} ]".center(width + 8).upper(), end="")
        # Print progress bar separator
        if i < len(step_list) - 1:
            print(">>>", end="")
    print("\n")

    return step_num + 1


def add_task(task_list):
    """
    Add task via manual process (one prompt per 'screen'),
    with progress bar displayed on each 'screen'.
    Current fields: title (req), description, due date, priority.

    :param task_list:       Dictionary of user tasks.

    :return:                none
    """
    # Print status bar
    step_num = 0
    step_list = ['Task Title', 'Description', 'Due Date', 'Priority', 'Task Added']
    step_num = print_progress_bar(step_list, step_num)

    # Task add intro
    print("\tFollow the prompts to add a title, description, due date, and priority for your task.\n\n"
          "\t( Tip! ) Only TITLE is required. Other fields may be left blank.\n"
          "\t( Tip! ) Editing: Tasks can be EDITED later!\n"
          "\t( Tip! ) Quick Add: Enter 'Q' on this screen to QUICK-ADD a task.\n"
          "\t                    Recommended for advanced users only.\n"
          "\t( Tip! ) Go Back: Enter 'B' to go BACK to your task list without saving.\n")

    # Get task name OR 'Q' for quick-add from user
    task_name = input("\n\tEnter a task name: ")
    # If user enters 'Q', go to quick-add
    if task_name.upper() == 'Q':
        clear_screen()
        add_task_quick(task_list)
        return
    # If user enters 'B', go back to view list
    if task_name.upper() == 'B':
        return
    # Validation for required task_name input
    while task_name == "":
        task_name = input("\n\tTask name is required\n\tEnter a task name: ")
        if task_name.upper() == 'B':
            return

    # Get description from user
    step_num = print_progress_bar(step_list, step_num)
    description = input("\n\tEnter a task description: ")
    if description.upper() == 'B':
        return

    # Get due date from user
    step_num = print_progress_bar(step_list, step_num)
    due_date = input("\n\tEnter a due date: ")
    if due_date.upper() == 'B':
        return
    # TODO: date validation (currently str)

    # Get priority from user
    step_num = print_progress_bar(step_list, step_num)
    priority = input("\n\tEnter a priority level: ")
    if priority.upper() == 'B':
        return
    # TODO: add validation for specified priorities

    # Save input into task_list, display confirmation
    save_new_task(task_list, task_name, description, due_date, priority)
    print_progress_bar(step_list, step_num)
    print("\n\t✓ Task added successfully!\n\n")
    time.sleep(1)


def add_task_quick(task_list):
    """
    Quick-add a task via single string in specified format.

    :param task_list:       Dictionary of user tasks.

    :return:                none
    """
    # Print instructions, get input
    print("> QUICK ADD:  Enter a task in the following format to quickly add a task:\n\n"
          "                 Task title//Task description//Due date//Priority\n\n"
          "              Recommended for advanced users only.\n\n"
          "              ( Tip! ) Only TITLE is required. Other fields may be left blank.\n"
          "              ( Tip! ) Tasks can be EDITED later!\n"
          "              ( Tip! ) Go back: Want to follow prompts instead?\n"
          "                       Enter 'B' to GO BACK.\n\n")
    quick_add_prompt = ("\t> Enter task in this format (or 'B' to GO BACK):\n"
                        "\tTask title//Task description//Due date//Priority\n\t")
    quick_input = input(quick_add_prompt)

    # If user input is 'B', go back to manual entry
    if quick_input.upper() == 'B':
        add_task(task_list)
        return
    # If user entered nothing, retry prompt
    while quick_input == "":
        quick_input = input("\n\t(!) Input required\n\tEnter task information or 'B' to go back: \n")

    # Parse string
    try:
        task_name, description, due_date, priority = quick_input.split("//")
    except ValueError:
        print("\n\t(!) Invalid input. Please try again.\n")
        add_task_quick(task_list)
        return

    # Save input into task_list, display confirmation
    save_new_task(task_list, task_name, description, due_date, priority)
    clear_screen()
    print("\n\t✓ Task added successfully!\n\n")
    time.sleep(1)


def save_new_task(task_list, task_name, description, due_date, priority):
    """
    Create new Task object with input task data and save task to user's list.

    :param task_list:       Dictionary of user tasks.
    :param task_name:       Input task name
    :param description:     Input task description
    :param due_date:        Input task due date
    :param priority:        Input task priority

    :return:                none
    """
    # Generate task ID
    if task_list != {}:
        new_task_id = max(task_list.keys()) + 1
    else:
        new_task_id = 1

    # Save task to dictionary
    new_task = Task(task_name, description, due_date, priority)
    task_list[new_task_id] = new_task

    # Save dictionary to file
    save_list(task_list, 'userlist.pkl')


def save_list(list_object, filename):
    """
    Saves input task list to file at specified filepath.
    Requires pickle module.

    :param list_object:     Dictionary of user tasks.
    :param filename:        Filepath for output

    :return:                none
    """
    with open(filename, 'wb') as outputfile:
        pickle.dump(list_object, outputfile)


class Task:
    """
    Represents a Task in the task list, with attributes.
    """
    def __init__(self, task_name, description, due_date, priority):
        self.task_name = task_name
        self.description = description
        self.due_date = due_date
        self.priority = priority

    def __repr__(self):
        return f"[ Task name: {self.task_name} || Description: {self.description} || Due date: {self.due_date} || Priority level: {self.priority} ]"


def view_tasks_menu(user_list, completed_task_list):
    """
    Navigation menu for under task view.

    :param user_list:               Dictionary of user tasks.
    :param completed_task_list:     Dictionary of completed tasks.

    :return:                        none
    """
    while True:
        list_is_populated = view_all_tasks()
        # If list found empty, return
        if not list_is_populated:
            return
        # Ask user for next step
        next_step_prompt = ("\nEnter 'A' to ADD a new item."
                            "\nEnter 'C' to mark a task as COMPLETE."
                            "\nEnter 'E' to EDIT a task."
                            "\nEnter 'M' to return to the MAIN MENU.\n\n")
        valid_next_steps = ['A', 'C', 'E', 'M']
        user_choice = get_input(next_step_prompt, valid_next_steps)

        # If user enters M, return to main menu
        if user_choice == 'M':
            clear_screen()
            break

        # If user enters A, add task
        elif user_choice == 'A':
            add_task(user_list)
            continue

        # If user enters E, edit task
        elif user_choice == 'E':
            task_id = int(get_input("\nTo EDIT a task, enter its TaskID: ", user_list))
            edit_task(task_id, user_list)
            continue

        # If user enters C, mark task as complete
        else:
            task_id = int(get_input("\nTo mark a task as COMPLETE, enter its TaskID: ", user_list))
            confirmation = input("\n(!) Are you sure you want to mark this task as completed?\n"
                                 "(!) THIS ACTION CANNOT BE REVERSED.\n"
                                 "\nEnter 'C' to COMPLETE the task or 'B' to go BACK to your list: ").upper()
            # If user confirms, complete task
            if confirmation == 'C':
                complete_task(task_id, user_list, completed_task_list)
            continue


def view_all_tasks():
    """
    View all tasks in saved task list.
    Requires pickle module.

    :param:     none

    :return:    True if tasks exist, False if file empty
    """
    clear_screen()
    # Print list if exists
    try:
        with open('userlist.pkl', 'rb') as readfile:
            user_list = pickle.load(readfile)
        # Print column headers
        print('{:<8} {:<20} {:<30} {:<15} {:15}'.format('TaskID', 'Task', 'Description', 'Due Date', 'Priority'))
        print("-" * (8+20+30+15+15))
        # Print all tasks
        for task in user_list:
            print('{:<8} {:<20} {:<30} {:<15} {:15}'.format(task, user_list[task].task_name, user_list[task].description, user_list[task].due_date, user_list[task].priority))
        # Return true
        return True
    # Return error if empty list
    except EOFError:
        print("Your to do list is empty!\n")
        return False


def edit_task(task_id, task_list):
    """
    Edit task via manual process (one prompt per 'screen'),
    with progress bar displayed on each 'screen'.
    Current fields: title (req), description, due date, priority.

    :param task_id:         ID of task to edit
    :param task_list:       Dictionary of user tasks.

    :return:                none
    """
    step_num = 0
    step_list = ['Edit Task Title', 'Edit Description', 'Edit Due Date', 'Edit Priority', 'Edit Completed']

    # Get task name from user
    step_num = print_progress_bar(step_list, step_num)
    task_name = input(f"\t>> Current task name: {task_list[task_id].task_name}\n\n"
                      f"\tTo leave task name as is, press enter.\n"
                      f"\tTo EDIT task name, enter a new task name: ")

    # Get description from user
    step_num = print_progress_bar(step_list, step_num)
    description = input(f"\t>> Current description: {task_list[task_id].description}\n\n"
                        f"\tTo leave description as is, press enter.\n"
                        f"\tTo EDIT description, enter a new description: ")

    # Get due date from user
    step_num = print_progress_bar(step_list, step_num)
    due_date = input(f"\t>> Current due date: {task_list[task_id].due_date}\n\n"
                      f"\tTo leave due date as is, press enter.\n"
                      f"\tTo EDIT due date, enter a new due date: ")
    # TODO: add date validation

    # Get priority from user
    step_num = print_progress_bar(step_list, step_num)
    priority = input(f"\t>> Current priority: {task_list[task_id].priority}\n\n"
                     f"\tTo leave priority as is, press enter.\n"
                     f"\tTo EDIT priority, enter a new priority: ")
    # TODO: add priority validation

    # Save edited attributes into task_list task
    # TODO: better way to write this?
    if task_name != '':
        task_list[task_id].task_name = task_name
    if description != '':
        task_list[task_id].description = description
    if due_date != '':
        task_list[task_id].due_date = due_date
    if priority != '':
        task_list[task_id].priority = priority

    # Save updated dictionary to file
    save_list(task_list, 'userlist.pkl')

    # Task edited successfully
    print_progress_bar(step_list, step_num)
    print("\n\t✓ Task edited successfully!\n\n")
    time.sleep(1)


def complete_task(task_id, user_list, completed_task_list):
    """
    Removes task from task list.
    # TODO: this could become move_list and could move completed tasks back to main list too

    :param task_id:                 ID of task to complete.
    :param user_list:               Dictionary of user tasks.
    :param completed_task_list:     Dictionary of completed user tasks.

    :return:                        none
    """
    # Move completed task to completed_task_list
    completed_task_list[task_id] = user_list[task_id]

    # Save completed_task_list
    save_list(completed_task_list, 'completed.pkl')

    # Delete task from user_list
    user_list.pop(task_id)

    # Save user_list
    save_list(user_list, 'userlist.pkl')

    # Confirm completed
    clear_screen()
    print("\n\t✓ Task successfully marked completed!\n\n")
    time.sleep(1)


def get_help():
    """
    Display help menu for app.
    Requires textwrap module for print formatting.

    :param:     none

    :return:    none
    """
    help_text = (
          "\nTO ADD a new task, enter 'A' from the home page, then follow the prompts to enter each field.\n"
          "\tTask name is the only required field\n"
          "\tYou can leave all other fields blank (just press enter)\n"
          "\tTasks can be EDITED or REMOVED (by marking as complete) later\n"

          "\nTo QUICK-ADD a new task:\n"
          "\t* Recommended for advanced users only.\n"
          "\t(1) Go to the ADD page by entering 'A' from the home page\n"
          "\t(2) Access the quick-add option by entering 'Q' from the ADD page\n"
          "\t(3) Enter a task in the following format:\n"
          "\t\tTask title//Task description//Due date//Priority\n"
          "\t* You must enter the '\\' delimiters correctly or the quick-add will fail.\n"
          "\t* To leave a field blank, just continue onto the next delimiters \n\t\t  (e.g. '\\\\' to skip one field)\n"

          "\nTo VIEW and manage all tasks on your list, enter 'V' from the main menu \nor anywhere else you see the prompt.\n"

          "\nTo mark a task as COMPLETE, enter 'C' from the VIEW tasks screen \nand follow the on-screen prompts.\n"
          "\t* Completing a task deletes it forever. It cannot be undone.\n"

          "\nTo EDIT a task, enter 'E' from the VIEW tasks screen \nand follow the on-screen prompts.\n"
          "\t* If you want to leave a field as is, just press enter when prompted to edit the field.\n"

          "\nTo QUIT the app, enter 'Q' from the main menu.\n")

    # Print help menu
    clear_screen()
    print("> HELP\n")
    print(textwrap.indent(help_text.strip(), '    '))

    # Exit to main menu prompt
    next_step = input("\n> Enter 'M' to return to the MAIN MENU.\n\n").upper()
    while next_step != 'M':
        next_step = input("\n> Enter 'M' to return to the MAIN MENU.\n\n").upper()
    clear_screen()

    return

