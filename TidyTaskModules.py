# Name: Arianne Taormina
# Course: CS361 - Software Engineering I
# Assignment: Portfolio Project with Microservice Implementation
# Date: Nov 30, 2025

# Description:  Modules for Main Program implementation.
#               Utilizes the following 5 microservices:
#               (1) Notification Service (small pool), (2) Analytics Service (small pool),
#               (3) Search Service (big pool), (4) Sort Service (big pool), (5) Filter Service (big pool)


import pickle, time, textwrap, zmq
from datetime import datetime


class Task:
    """
    Represents a Task in the task list, with attributes.
    """
    def __init__(self, task_id, task_name, description, due_date, priority, status='incomplete'):
        self.id = task_id
        self.task_name = task_name
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = status

    def get_attribute(self, attribute_name):
        """
        Returns value of the given attribute.
        Raises AttributeError if the attribute does not exist.
        """
        return getattr(self, attribute_name)

    def set_attribute(self, attribute_name, value):
        """
        Sets value of the given attribute to the given value.
        """
        setattr(self, attribute_name, value)

    def set_complete(self):
        """
        Mark task as complete.
        """
        self.status = 'complete'

    def convert_to_dict(self, purpose='export'):
        """
        Convert Task object to purpose-specific dictionary
        for JSON export or microservice compatibility.

        :param purpose:     Intended purpose for converted dict
        :return:            Dictionary of Task attribute key/value pairs
        """
        # Designate keys based on intended use for dictionary
        task_id_key = "event_id" if purpose == "notification" else "id"
        task_name_key = "event_name" if purpose == "notification" else "task_name"

        return {
            task_id_key: self.id,
            task_name_key: self.task_name,
            "description": self.description,
            "due_date": self.due_date.strftime("%Y-%m-%d") if self.due_date else "", # Date object converted to string
            "priority": int(self.priority) if self.priority != "" else "",
            "status": self.status
        }

    def __str__(self):
        return (f"[ Task name: {self.task_name} | "
                f"Description: {self.description or 'None'} | "
                f"Due date: {self.due_date or 'None'} | "
                f"Priority: {self.priority or 'None'} | "
                f"Status: {self.status} ]")


def print_welcome():
    """
    Print title and welcome message for Tidy Task app.
    """
    clear_screen()
    print("\nT I D Y   T A S K\n")
    print("The simple app for tracking the tasks on your to do list.\n"
          "Add, view, edit, and complete tasks on your to do list.\n\n"
          "* New *\n"
          "   Sort, search, and filter tasks\n"
          "   Get your completion stats\n"
          "   Keep track of your overdue tasks")
    print("_" * 58, "\n")


def import_list(filename):
    """
    Returns existing saved list, or blank list if none found.
    Requires pickle module.

    :param filename:    filepath of saved list
    :return:            user list (dict) or {}
    """
    try:
        with open(filename, 'rb') as readfile:
            return pickle.load(readfile)
    # If no saved list found, create blank list
    except FileNotFoundError:
        with open(filename, 'wb') as outputfile:
            if filename == 'userlist.pkl':
                print("No saved to do list found. New list has been created.\n")
            return {}
    # If file found but blank, create blank list
    except EOFError:
        return {}


def main_menu():
    """
    Display main menu and get validated user input for next action.

    :return:    user choice for next action (str)
    """
    start_prompt = ("Enter any of these commands to continue...\n\n"
                    "View: 'V' to VIEW and manage all tasks on your to do list\n"
                    "Add:  'A' to ADD a new task\n"
                    "Help: 'H' to get HELP with the app\n"
                    "Quit: 'Q' to QUIT the app\n\n"
                    ">> ")
    valid_responses = ['V', 'A', 'H', 'Q']
    return get_input(start_prompt, valid_responses)


def main_menu_route(user_choice, user_list):
    """
    Route to the correct function from main menu based on input user_choice.

    :param user_choice:     User-entered choice (str)
    :param user_list:       Dictionary of user tasks
    :return:                False if Q to quit, True otherwise
    """
    if user_choice == 'A':
        add_task(user_list)
        task_menu(user_list)
    elif user_choice == 'V':
        task_menu(user_list)
    elif user_choice == 'H':
        get_help()
    elif user_choice == 'Q':
        clear_screen()
        print("You have exited Tidy Task. Good luck with your tasks!")
        return False
    return True


def get_input(prompt, valid_responses):
    """
    Get, validate, and return user input for navigation prompts in app.

    :param prompt:              prompt string
    :param valid_responses:     list of valid responses for input validation
    :return:                    user input response to prompt (str)
    """
    while True:
        user_response = input(prompt).strip()

        if user_response.isdigit():
            user_response = int(user_response)
        else:
            user_response = user_response.upper()

        if user_response in valid_responses:
            return user_response
        print("Invalid input.")


def get_task_id_keys(user_list):
    """
    Get list of keys for incomplete tasks

    :param user_list:   Dictionary of user tasks
    :return:            Valid task ID
    """
    incomplete_task_keys = []
    for key, task in user_list.items():
        if task.status == 'incomplete':
            incomplete_task_keys.append(key)
    return incomplete_task_keys


def clear_screen():
    """
    Simulates clearing of CLI for cleaner UI.
    """
    print('\n' * 100)


def pause_before_return(messages=None):
    """
    Await user input to return to task list.

    :param messages:    Messages to print
    """
    print()
    if messages:
        for msg in messages:
            print(msg)
    input("\nPress ENTER to return to the task list...")
    clear_screen()


def view_task_list(sublist=None, title=' '):
    """
    View incomplete tasks in saved task list or temporary sublist.
    Requires pickle module.

    :param sublist:     List of tasks other than saved list
    :param title:       Title of task list
    :return:            True if tasks to display, False otherwise
    """
    no_incomplete = True
    try:
        # If no task_list input, load saved list
        if sublist is None:
            with open('userlist.pkl', 'rb') as readfile:
                user_list = pickle.load(readfile)
        else:
            user_list = sublist

        col_widths = [8, 25, 30, 15, 15]
        table_headers = ['TaskID', 'Task', 'Description', 'Due Date', 'Priority']
        print_table_row(table_headers, col_widths, title)

        # Print (incomplete) tasks in formatted table
        for task in user_list:
            if user_list[task].status == 'incomplete':
                formatted_date = user_list[task].due_date.strftime('%b %d, %Y') if user_list[task].due_date else "" # Format: 'Nov 13, 2025'
                priority_map = {'1': 'High', '2': 'Medium', '3': 'Low'}
                aliased_priority = priority_map.get(str(user_list[task].priority), "")
                row_data = [task, user_list[task].task_name, user_list[task].description, formatted_date, aliased_priority]
                print_table_row(row_data, col_widths)
                no_incomplete = False

    # Return False if no incomplete tasks or empty list
        if no_incomplete and sublist is None:
            print("Your to do list is empty!\n")
            return False
        return True
    except (EOFError, FileNotFoundError):
        print("Your to do list is empty!\n")
        return False


def print_table_row(row_data, col_widths, header=""):
    """
    Print table header or row of table data, formatted to specified col widths.

    :param row_data:    Data to print in row
    :param col_widths:  Width of cols in table view
    :param header:      Table title, if printing header row
    """
    if header:
        print(f"\n{header.upper()}\n")

    format_col_widths = [f"{{:<{width}}}" for width in col_widths]
    format_str = " ".join(format_col_widths)
    print(format_str.format(*row_data))

    if header:
        print("-" * sum(col_widths))


def task_menu(user_list):
    """
    Navigation menu for beneath task list view.

    :param user_list:   Dictionary of user tasks
    """
    clear_screen()
    while True:
        # Return if empty or no pending tasks
        if not view_task_list():
            return

        user_choice = get_task_menu_choice()
        # Route to correct function, or exit to Main Menu
        if not route_choice(user_choice, user_list):
            return


def get_task_menu_choice():
    """
    Get user choice for task list navigation menu.

    :return:    User choice (str)
    """
    next_step_prompt = (
        "\nEnter 'A' to ADD a new item."
        "\nEnter 'C' to mark a task as COMPLETE."
        "\nEnter 'E' to EDIT a task."
        "\nEnter 'O' to view OVERDUE tasks."
        "\nEnter 'SE' to SEARCH tasks."
        "\nEnter 'ST' to SORT tasks."
        "\nEnter 'F' to FILTER tasks."
        "\nEnter 'P' to view PROGRESS stats."
        "\nEnter 'M' to return to the MAIN MENU.\n\n>> "
    )
    valid_next_steps = ['A', 'C', 'E', 'O', 'SE', 'ST', 'F', 'P', 'M']
    return get_input(next_step_prompt, valid_next_steps)


def route_choice(user_choice, user_list):
    """
    Route to correct function from task view list based on input user_choice.

    :param user_choice:     User-entered choice (str)
    :param user_list:       Dictionary of user tasks
    :return:                False if user_choice == 'M' (main menu), True otherwise
    """
    if user_choice == 'M':
        clear_screen()
        return False
    elif user_choice == 'A':
        add_task(user_list)
    elif user_choice == 'E':
        task_id = get_input("\nTo EDIT a task, enter its TaskID: ", get_task_id_keys(user_list))
        edit_task(task_id, user_list)
    elif user_choice == 'O':
        overdue_msgs = get_overdue_tasks(user_list)
        pause_before_return(overdue_msgs)
    elif user_choice == 'SE':
        search_tasks(user_list)
        pause_before_return()
    elif user_choice == 'ST':
        sort_tasks(user_list)
    elif user_choice == 'F':
        filter_tasks(user_list)
        pause_before_return()
    elif user_choice == 'P':
        print('\n\t', get_completion_rate(user_list))
        pause_before_return()
    elif user_choice == 'C':
        complete_task_warn(user_list)
    return True


def print_progress_bar(step_list, step_num):
    """
    Display progress bar for steps in process, with emphasis on current step.
    Returns next step number to print next progress bar with correct emphasis.

    :param step_list:   List of steps in process
    :param step_num:    Number of current step in list
    :return:            step_num + 1
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
    """
    new_task_data = {}
    step_num = 0
    step_list = ['Task Title', 'Description', 'Due Date', 'Priority', 'Task Added']
    attributes = ['task_name', 'description', 'due_date', 'priority']

    print("\tFollow the prompts to add a title, description, due date, and priority for your task.\n\n"
          "\t\t( Tip! ) Only TITLE is required. Other fields may be left blank.\n"
          "\t\t( Tip! ) Editing: Tasks can be EDITED later!\n"
          "\t\t( Tip! ) Quick Add: Enter 'Q' on this screen to QUICK-ADD a task.\n"
          "\t\t                    Recommended for advanced users only.\n"
          "\t\t( Tip! ) Go Back: Enter 'B' to go BACK to your task list without saving at any time.\n")

    hint_map = {
        "task_name": " (required)",
        "description": "",
        "due_date": " (YYYY-MM-DD)",
        "priority": " (1 for High, 2 for Medium, 3 for Low)",
    }

    for attribute in attributes:
        step_num = print_progress_bar(step_list, step_num)
        label = attribute.replace("_", " ")
        hint = hint_map[attribute]
        prompt_string = f"\n\tEnter a {label}{hint}: "
        allow_blank = False if attribute == "task_name" else True

        value = get_validated_task_input(prompt_string, attribute, allow_blank, allow_back=True)

        if attribute == "task_name" and value.upper() == 'Q':
            clear_screen()
            add_task_quick(task_list)
            return

        if value == "B":
            clear_screen()
            return

        new_task_data[attribute] = value

    save_new_task(
        task_list,
        new_task_data.get("task_name"),
        new_task_data.get("description"),
        new_task_data.get("due_date"),
        new_task_data.get("priority")
    )

    print_progress_bar(step_list, step_num)
    print("\n\t✓ Task added successfully!\n\n")
    time.sleep(1)
    clear_screen()


def add_task_quick(task_list):
    """
    Quick-add a task via single string in specified format.

    :param task_list:       Dictionary of user tasks.

    :return:                none
    """
    print("> QUICK ADD:  Enter a task in the following format to quickly add a task:\n\n"
          "                 Task title/Task description/Due date/Priority\n\n"
          "              Recommended for advanced users only.\n\n"
          "              ( Tip! ) Only TITLE is required. Other fields may be left blank.\n"
          "              ( Tip! ) Tasks can be EDITED later!\n"
          "              ( Tip! ) Go back: Want to follow prompts instead?\n"
          "                       Enter 'B' to GO BACK.\n\n")
    quick_add_prompt = (
        "\t> Enter task in this format (or 'B' to GO BACK):\n"
        "\tTask title/Task description/Due date (YYYY-MM-DD)/Priority (1, 2, 3)\n\t"
    )

    while True:
        quick_input = input(quick_add_prompt).strip()

        # If user input is 'B', go back to manual entry
        if quick_input.upper() == 'B':
            add_task(task_list)
            return

        # If user entered nothing, retry prompt
        if quick_input == "":
            print("\n\t(!) Input required.\n")
            continue

        valid_quick_input = validate_quick_add_input(quick_input, '/')
        if valid_quick_input:
            task_name, description, due_date, priority = valid_quick_input
            save_new_task(task_list, task_name, description, due_date, priority)
            clear_screen()
            print("\n\t✓ Task added successfully!\n\n")
            time.sleep(1)
            clear_screen()
            return


def get_validated_task_input(prompt, field, allow_blank=True, allow_back=True):
    """
    Get validated user input from user for task field input.

    :param prompt:          Prompt string
    :param field:           Field to validate
    :param allow_blank:     If True, allow blank field
    :param allow_back:      If True, allow input to go back
    :return:                Validated input, "" if field blank, or "B" to go back
    """
    while True:
        user_input = input(prompt).strip()
        if allow_back and user_input.upper() == "B":
            return "B"
        if allow_blank and user_input == "":
            return ""
        elif not allow_blank and user_input == "":
            print("\n\t(!) This field is required. Please enter a value.\n")
            continue
        if field == "due_date":
            try:
                return validate_date_input(user_input)
            except ValueError as e:
                print(f"\n\t(!) {e}\n")
                continue
        elif field == "priority":
            try:
                return validate_priority_input(user_input)
            except ValueError as e:
                print(f"\n\t(!) {e}\n")
                continue
        return user_input


def validate_date_input(date_input):
    """
    Validate date input string and convert to date object in YYYY-MM-DD format.
    Raise ValueError if invalid.

    :param date_input:  User input date string
    :return:            Valid date object in YYYY-MM-DD format (or raise ValueError)
    """
    try:
        return datetime.strptime(date_input, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")


def validate_priority_input(priority_input):
    """
    Validate priority input (1, 2, 3) (int).
    Raise ValueError if invalid.

    :param priority_input:  User input priority
    :return:            Valid priority input (or raise ValueError)
    """
    try:
        priority = int(priority_input)
        if priority in (1, 2, 3):
            return priority
        else:
            raise ValueError("Invalid priority input. Please enter 1, 2, or 3.")
    except ValueError:
        raise ValueError("Invalid priority input. Please enter 1, 2, or 3.")


def validate_quick_add_input(quick_input, delimiter):
    """
    Parse and validate quick-add input string.

    :param quick_input:     User input string
    :param delimiter:       Delimiter used in quick add string (str)
    :return:                task_name, description, due_date, priority if valid, else None
    """
    try:
        # Parse string
        task_name, description, due_date, priority = quick_input.split(delimiter)

        if not task_name.strip():
            print("\n\t(!) Task title is required. Please try again.\n")
            return None

        if due_date.strip():
            try:
                due_date = validate_date_input(due_date.strip())
            except ValueError as e:
                print(f"\n\t(!) {e}\n")
                return None
        else:
            due_date = ""

        if priority.strip():
            try:
                priority = validate_priority_input(priority.strip())
            except ValueError as e:
                print(f"\n\t(!) {e}\n")
                return None
        else:
            priority = ""

        return task_name.strip(), description.strip(), due_date, priority

    except Exception:
        print("\n\t(!) Invalid input format. Please try again.\n")
        return None


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

    # Save task and updated dictionary
    new_task = Task(new_task_id, task_name, description, due_date, priority)
    task_list[new_task_id] = new_task
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


def edit_task(task_id, task_list):
    """
    Edit task via manual process (one prompt per 'screen'),
    with progress bar displayed on each 'screen'.
    Fields: title (req), description, due date, priority.

    :param task_id:         ID of task to edit
    :param task_list:       Dictionary of user tasks.
    """
    step_num = 0
    step_list = ['Edit Task Title', 'Edit Description', 'Edit Due Date', 'Edit Priority', 'Edit Completed']
    attributes = ['task_name', 'description', 'due_date', 'priority']

    for attribute in attributes:
        step_num = print_progress_bar(step_list, step_num)
        label = attribute.replace("_", " ")
        current_value = task_list[task_id].get_attribute(attribute)
        hint = (
            " (YYYY-MM-DD)" if attribute == 'due_date'
            else " (1 for High, 2 for Medium, 3 for Low)" if attribute == 'priority'
            else ""
        )
        prompt_string = (
            f"\t>> Current {label}: {current_value}\n\n"
            f"\tTo leave {label} as is, press enter.\n"
            f"\tTo EDIT {label}, enter a new {label}{hint}: "
        )

        updated_value = get_validated_task_input(prompt_string, attribute, allow_blank=True, allow_back=False)
        if updated_value:
            task_list[task_id].set_attribute(attribute, updated_value)

    save_list(task_list, 'userlist.pkl')

    print_progress_bar(step_list, step_num)
    print("\n\t✓ Task edited successfully!\n\n")
    time.sleep(1)
    clear_screen()


def complete_task_warn(user_list):
    """
    Warning and confirmation before marking task as completed.
    Route to complete task if confirmed.

    :param user_list:       Dictionary of user tasks
    """
    task_id = int(get_input("\nTo mark a task as COMPLETE, enter its TaskID: ", get_task_id_keys(user_list)))
    confirmation = input("\n(!) Are you sure you want to mark this task as completed?\n"
                         "(!) THIS ACTION CANNOT BE REVERSED.\n"
                         "\nEnter 'C' to COMPLETE the task or 'B' to go BACK to your list: ").upper()
    # If user confirms, complete task
    if confirmation == 'C':
        complete_task(task_id, user_list)


def complete_task(task_id, user_list):
    """
    Marks task on task list as complete.

    :param task_id:     ID of task to complete
    :param user_list:   Dictionary of user tasks
    """
    user_list[task_id].set_complete()
    save_list(user_list, 'userlist.pkl')

    clear_screen()
    print("\n\t✓ Task successfully marked completed!\n\n")
    time.sleep(1)
    clear_screen()


def create_json_data(user_list, purpose='export'):
    """
    Compile task list data into purpose-specific JSON format for microservice use.

    :param user_list:   Dictionary of user tasks
    :param purpose:     Intended purpose for JSON data
    :return:
    """
    json_data = []
    for task in user_list:
        task_as_dict = user_list[task].convert_to_dict(purpose=purpose)
        json_data.append(task_as_dict)
    return json_data


def rebuild_task_dict(json_data, purpose='export'):
    """
    Rebuild dictionary of Task object from JSON data.

    :param json_data:   JSON data to rebuild dict from
    :param purpose:     Purpose data was used for (for correct key names)
    :return:            Dictionary of Task objects with ID keys
    """
    task_dict = {}
    for task in json_data:
        task_object = convert_dict_to_task(task, purpose=purpose)
        task_dict[task_object.id] = task_object
    return task_dict


def convert_dict_to_task(item, purpose='export'):
    """
    Convert purpose-specific dictionary to Task object.

    :param item:        Dictionary of task attributes
    :param purpose:     Purpose data was used for (for correct key names)
    :return:            Dictionary of Task object with ID key
    """
    # Designate keys based on intended use for dictionary
    task_id_key = "event_id" if purpose == "notification" else "id"
    task_name_key = "event_name" if purpose == "notification" else "task_name"

    return Task(
        int(item[task_id_key]),
        item[task_name_key],
        item["description"] if item["description"] else "",
        datetime.strptime(item["due_date"], "%Y-%m-%d").date() if item["due_date"] else "",
        int(item["priority"]) if item["priority"] else "",
        item["status"]
    )


def zmq_connect(port):
    """
    Create ZMQ context, connect on specified port.

    :param port:    Port number for connection
    :return:        Socket
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{port}")
    return socket


def get_overdue_tasks(user_list):
    """
    Get list of overdue tasks on task list.
    Utilizes Notification Microservice, connecting via ZMQ on port 5556.

    :param user_list:       Dictionary of user tasks
    :return:                List of overdue task messages or error
    """
    # Send request via port 5556
    socket = zmq_connect(5556)
    task_data = create_json_data(user_list, 'notification')
    request = {
        "notification_type": "overdue",
        "event_data": task_data
    }
    socket.send_json(request)

    # Receive response, return overdue tasks
    response = socket.recv_json()
    overdue_tasks = []
    if response["status"] == "success":
        for notification in response["notifications"]:
            overdue_tasks.append(notification["message"])
        return overdue_tasks
    return ["Error returning overdue tasks."]


def get_completion_rate(user_list):
    """
    Get % of tasks completed over life of task list.
    Utilizes Analytics Microservice, connecting via ZMQ on port 5555.

    :param user_list:       Dictionary of user tasks
    :return:                Result message
    """
    # Send request via port 5555
    socket = zmq_connect(5555)
    task_data = create_json_data(user_list, 'get_completion_rate')
    request = {
        "metric_type": "get_completion_rate",
        "event_type": "task",
        "event_data": task_data
    }
    socket.send_json(request)

    response = socket.recv_json()
    if response["status"] == "success":
        return f"{response["result"]*100:.0f}% of tasks completed"
    return "Error analyzing completion rate."


def search_tasks(user_list):
    """
    Get tasks that contain search criteria in given "column."

    :param user_list:   Dictionary of user tasks
    """
    socket = zmq_connect(5558)

    search_field = get_field_name('search')
    search_term = input("Enter search term: ")
    if search_field == 'priority' and str(search_term).lower() in ('high', 'medium', 'low'):
        priority_map = {"high": "1", "medium": "2", "low": "3"}
        search_term = priority_map[str(search_term).lower()]

    request = {
        "search_type": "basic_search",
        "search_field": search_field,
        "search_term": search_term,
        "data": create_json_data(user_list)
    }

    print("\nSearching...")
    socket.send_json(request)

    response = socket.recv_json()
    if response["status"] == "success": #
        clear_screen()
        count = sum(1 for task in response["results"] if task["status"] == "incomplete")
        match_or_matches = "matches" if count != 1 else "match"
        result_list = rebuild_task_dict(response["results"])
        view_task_list(result_list, f"SEARCH RESULTS: {count} {match_or_matches} found")
    else:
        clear_screen()
        print("\nSEARCH RESULTS: No matches found.")


def get_field_name(purpose):
    """
    Maps user-entered int to existing key,
    with purpose-specific message (for search, sort, filter).

    :return:    key (str)
    """
    purpose_str = (
        "search within" if purpose=="search"
        else "sort by" if purpose=="sort"
        else "filter by"
    )
    prompt = (
        f"\nEnter [ 1 for TaskId, 2 for Task Name, 3 for Description, 4 for Date, 5 for Priority ]\n\n"
        f"Column to {purpose_str}: "
    )
    search_field_input = get_input(prompt, [1, 2, 3, 4, 5])
    search_field_map = {1: "id", 2: "task_name", 3: "description", 4: "due_date", 5: "priority"}
    return search_field_map[int(search_field_input)]


def sort_tasks(user_list):
    """
    Sort list of tasks by given "column" in ascending or descending order,
    based on user input.

    :param user_list:   Dictionary of user tasks
    """
    socket = zmq_connect(5559)

    sort_field = get_field_name('sort')
    sort_type_map = {
        'id': 'sort_int',
        'task_name': 'sort_string',
        'description': 'sort_string',
        'due_date': 'sort_string',
        'priority': 'sort_string',
    }
    sort_type = sort_type_map[sort_field]
    sort_order = get_input("Ascending ('asc') or Descending ('desc'): ", ["ASC", "DESC"]).lower()
    priority_reverse_map = {"asc": "desc", "desc": "asc"}
    sort_order = priority_reverse_map[sort_order] if sort_field == "priority" else sort_order

    request = {
        "sort_type": sort_type,
        "sort_field": sort_field,
        "sort_order": sort_order,
        "data": create_json_data(user_list)
    }
    socket.send_json(request)
    response = socket.recv_json()

    # Overwrite existing list
    sorted_list = rebuild_task_dict(response["results"])
    user_list.clear()
    user_list.update(sorted_list)
    save_list(user_list, 'userlist.pkl')
    clear_screen()


def filter_tasks(user_list):
    """
    Get tasks that fall within filter criteria in any number of columns,
    based on user input.

    :param user_list:   Dictionary of user tasks
    """
    socket = zmq_connect(5560)

    filter_list = get_filter_list()
    logical_op = get_input(
        "\nDo you want to match ALL filters ('all' or 'and') or ANY filters ('any' or 'or)? ",
    ["ALL", "AND", "ANY", "OR"]
    )
    logical_op = "AND" if logical_op in ['ALL', 'AND'] else "OR"
    request = {
        "filter_type": "basic_filter",
        "data": create_json_data(user_list),
        "filters": filter_list,
        "logical_op": logical_op
    }

    print("\nFiltering...")
    socket.send_json(request)
    response = socket.recv_json()
    count = sum(1 for task in response["results"] if task["status"] == "incomplete")
    if response["status"] == "success" and count != 0:
        clear_screen()
        task_or_tasks = "tasks" if count != 1 else "task"
        result_list = rebuild_task_dict(response["results"])
        view_task_list(result_list, f"FILTERED TASKS: {count} {task_or_tasks}")
    else:
        clear_screen()
        print("\nFilter RESULTS: No matches found.")


def get_filter_list():
    """
    Get list of filters from user for filter_tasks.

    :return:    List of filters.
    """
    filters = []
    while True:
        field_name = get_field_name('filter')

        if field_name == 'due_date':
            operator = get_input(
                "\nEnter the operator for the filter ('is', 'contains', 'between'): ",
                ["IS", "CONTAINS", "BETWEEN"]
            ).lower()
        else:
            operator = get_input(
                "\nEnter the operator for the filter ('is', 'contains'): ",
                ["IS", "CONTAINS"]
            ).lower()
        operator = "==" if operator == "is" else operator

        if operator == "between":
            value1 = input("\nEnter the first value:  ")
            value2 = input("Enter the second value: ")
            value = [value1, value2]
        else:
            value = input("\nEnter value to filter by: ")
            if field_name == 'priority' and str(value).lower() in ('high', 'medium', 'low'):
                priority_map = {"high": "1", "medium": "2", "low": "3"}
                value = priority_map[str(value).lower()]

        filters.append({
            "field_name": field_name,
            "operator": operator,
            "value": value
        })

        another = get_input("\nDo you want to add another filter? (y/n): ", ["Y", "N"])
        if another == "N":
            break

    return filters


def get_help():
    """
    Display help menu for app.
    Requires textwrap module for print formatting.
    """
    help_text = (
        "\nTo VIEW and manage all tasks on your list, enter 'V' from the main menu \nor anywhere else you see the prompt.\n"
        
        "\nTO ADD a new task, enter 'A' from the home page or the task view page,\n"
        "then follow the prompts to enter each field.\n"
        "\tTask name is the only required field\n"
        "\tYou can leave all other fields blank (just press enter)\n"
        "\tTasks can be EDITED or REMOVED (by marking as complete) later\n"

        "\nTo QUICK-ADD a new task:\n"
        "\t* Recommended for advanced users only.\n"
        "\t(1) Go to the ADD page by entering 'A' from the home page or task page\n"
        "\t(2) Access the quick-add option by entering 'Q' from the ADD page\n"
        "\t(3) Enter a task in the following format:\n"
        "\t\tTask title/Task description/Due date/Priority\n"
        "\t* You must enter the '/' delimiters correctly or the quick-add will fail.\n"
        "\t* To leave a field blank, just continue onto the next delimiters \n\t\t  (e.g. '//' to skip one field)\n"

        "\nTo mark a task as COMPLETE, enter 'C' from the VIEW tasks screen \nand follow the on-screen prompts.\n"
        "\t* Completing a task removes it forever. This cannot be undone.\n"

        "\nTo EDIT a task, enter 'E' from the VIEW tasks screen \nand follow the on-screen prompts.\n"
        "\t* If you want to leave a field as is, just press ENTER when prompted to edit the field.\n"
        
        "\nTo view OVERDUE tasks, enter 'O' from the VIEW tasks screen.\n"
        
        "\nTo SEARCH tasks, enter 'SE' from the VIEW tasks screen \nand follow the on-screen prompts.\n"
        
        "\nTo SORT your task list, enter 'ST' from the VIEW tasks screen \nand follow the on-screen prompts.\n"
        "\t* This overrides the sort order of your saved list.\n"
        
        "\nTo FILTER your task list, enter 'F' from the VIEW tasks screen \nand follow the on-screen prompts.\n"
        
        "\nTo see your PROGRESS STATS (the % of tasks you've completed so far), "
        "\nenter 'P' from the VIEW tasks screen and follow the on-screen prompts.\n"

        "\nTo QUIT the app, enter 'Q' from the main menu.\n")

    clear_screen()
    print("> HELP\n")
    print(textwrap.indent(help_text.strip(), '    '))

    # Exit to main menu prompt
    next_step = input("\n> Enter 'M' to return to the MAIN MENU.\n\n").upper()
    while next_step != 'M':
        next_step = input("\n> Enter 'M' to return to the MAIN MENU.\n\n").upper()
    clear_screen()
    return
