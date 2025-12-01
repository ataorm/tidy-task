# Name: Arianne Taormina
# Course: CS361 - Software Engineering I
# Assignment: Portfolio Project with Microservice Implementation
# Date: Nov 30, 2025

# Description:  To do list app with add, edit, complete, view, search, sort, filter,
#               overdue summary, and analytics functionality.
#               Contains examples of all Inclusivity Heuristics.
#               Utilizes the following 5 microservices:
#               (1) Notification Service (small pool), (2) Analytics Service (small pool),
#               (3) Search Service (big pool), (4) Sort Service (big pool), (5) Filter Service (big pool)


from TidyTaskModules import print_welcome, import_list, main_menu, main_menu_route

def main():
    print_welcome()
    while True:
        user_list = import_list('userlist.pkl')
        main_menu_response = main_menu()
        continue_app = main_menu_route(main_menu_response, user_list)
        if not continue_app:
            break

if __name__ == "__main__":
    main()
