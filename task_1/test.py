from collections import UserDict
from typing import List
from datetime import datetime, timedelta
import pickle
from abc import ABC, abstractmethod


class Field:
    def __init__(self, value):
        self.value = value

        if not self.is_valid():
            raise ValueError

    def __str__(self):
        return str(self.value)

    def is_valid(self):
        return True


class Name(Field):
    pass


class Phone(Field):
    def is_valid(self):
        return len(self.value) == 10 and self.value.isdigit()


class Birthday(Field):
    def __init__(self, value: str):
        try:
            super().__init__(datetime.strptime(value, "%d.%m.%Y").date())
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Birthday | None = None

    def __str__(self):
        return (f"Contact name: {self.name}, phones: {"; ".join(list(map(lambda phone: str(phone), self.phones)))}, "
                f"birthday: {self.birthday}")

    def __find_phone_index__(self, phone_str):
        phone_index = None

        for i in range(len(self.phones)):
            if self.phones[i].value == phone_str:
                phone_index = i

        return phone_index

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        phone_index = self.__find_phone_index__(phone)

        if phone_index is None:
            raise ValueError
        else:
            del self.phones[phone_index]

    def edit_phone(self, old_phone: str, new_phone: str):
        phone_index = self.__find_phone_index__(old_phone)

        if phone_index is None:
            raise ValueError
        else:
            self.phones[phone_index] = Phone(new_phone)

    def find_phone(self, phone: str):
        phone_index = self.__find_phone_index__(phone)

        if phone_index is None:
            raise ValueError
        else:
            return self.phones[phone_index]

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)


class AddressBook(UserDict[str, Record]):
    def __str__(self):
        return "\n".join(map(str, self.data.values()))

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        if name in self.data.keys():
            return self.data[name]
        else:
            return None

    def delete(self, name: str):
        if name in self.data.keys():
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        date_today = datetime.today().date()
        date_today_plus_week = date_today + timedelta(days=7)

        for record in self.data.values():
            birthday = record.birthday.value.replace(year=date_today.year)

            if date_today.timetuple().tm_yday <= birthday.timetuple().tm_yday <= date_today_plus_week.timetuple().tm_yday:
                birthday_day_of_week = birthday.timetuple().tm_wday
                congratulation_date = birthday

                if birthday_day_of_week == 5 or birthday_day_of_week == 6:
                    next_monday = birthday + timedelta(days=7 - birthday.timetuple().tm_wday)
                    congratulation_date = next_monday

                upcoming_birthdays.append(
                    {"name": record.name.value, "congratulation_date": congratulation_date.strftime("%d.%m.%Y")})

        return upcoming_birthdays


def input_error(func):
    def inner(args, book):
        try:
            return func(args, book)
        except ValueError:
            return "Invalid arguments."
        except IndexError:
            return "Give me a username."
        except KeyError:
            return f"{args} doesn't exist."

    return inner


def parse_input(user_input: str):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()

    return cmd, *args


class ChatBot(ABC):
    def __init__(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as file:
                self.book = pickle.load(file)
        except FileNotFoundError:
            self.book = AddressBook()

    @abstractmethod
    def get_greeting(self):
        pass

    @abstractmethod
    @input_error
    def add_contact(self, args: List[str]):
        pass

    @abstractmethod
    @input_error
    def change_phone(self, args: List[str]):
        pass

    @abstractmethod
    @input_error
    def get_phones(self, args: List[str]):
        pass

    @abstractmethod
    def get_all_contacts(self):
        pass

    @abstractmethod
    @input_error
    def add_birthday(self, args):
        pass

    @abstractmethod
    @input_error
    def show_birthday(self, args):
        pass

    @abstractmethod
    def birthdays(self):
        pass

    @abstractmethod
    def get_good_bye(self):
        pass

    def save_data(self, filename="addressbook.pkl"):
        with open(filename, "wb") as file:
            pickle.dump(self.book, file)


class SimpleChatBot(ChatBot):
    def get_greeting(self):
        return "How can I help you?"

    def add_contact(self, args: List[str]):
        name, phone = args
        record = self.book.find(name)

        if not record:
            record = Record(name)

        record.add_phone(phone)
        self.book.add_record(record)

        return "Contact added."

    def change_phone(self, args: List[str]):
        name, old_phone, new_phone = args
        record = self.book.find(name)

        if not record:
            return f"{name} doesn't exists. Add it before changing it."

        record.edit_phone(old_phone, new_phone)

        return "Contact updated."

    def get_phones(self, args: List[str]):
        name = args[0]
        record = self.book.find(name)

        if not record:
            return f"{name} doesn't exist."

        return record.phones

    def get_all_contacts(self):
        if len(self.book.data) == 0:
            return "Contacts list is empty."

        return self.book

    def add_birthday(self, args):
        name, birthday = args
        record = self.book.find(name)

        if not record:
            record = Record(name)
            self.book.add_record(record)

        record.add_birthday(birthday)

        return "Birthday added."

    def show_birthday(self, args):
        name = args[0]
        record = self.book.find(name)

        if not record:
            return f"{name} doesn't exist."

        if not record.birthday:
            return f"{name} doesn't have birthday."

        return record.birthday

    def birthdays(self):
        if not self.book.data:
            return "Contacts list is empty."

        return self.book.get_upcoming_birthdays()

    def get_good_bye(self):
        return "Good bye!"


class AdvancedChatBot(ChatBot):
    def add_contact(self, args: List[str]):
        return "Non implemented."

    def change_phone(self, args: List[str]):
        return "Non implemented."

    def get_phones(self, args: List[str]):
        return "Non implemented."

    def get_all_contacts(self):
        return "Non implemented."

    def add_birthday(self, args):
        return "Non implemented."

    def show_birthday(self, args):
        return "Non implemented."

    def birthdays(self):
        return "Non implemented."

    def get_good_bye(self):
        return "Non implemented."

    def get_greeting(self):
        return "Hello from advanced bot. How can I help you?"


def main():
    chat_bot = SimpleChatBot()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        cmd, *args = parse_input(user_input)

        if cmd == "hello":
            print(chat_bot.get_greeting())
        elif cmd == "add":
            print(chat_bot.add_contact(args))
        elif cmd == "change":
            print(chat_bot.change_phone(args))
        elif cmd == "phone":
            print(chat_bot.get_phones(args))
        elif cmd == "add-birthday":
            print(chat_bot.add_birthday(args))
        elif cmd == "show-birthday":
            print(chat_bot.show_birthday(args))
        elif cmd == "birthdays":
            print(chat_bot.birthdays())
        elif cmd == "all":
            print(chat_bot.get_all_contacts())
        elif cmd == "close" or cmd == "exit":
            print(chat_bot.get_good_bye())
            chat_bot.save_data()
            break
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
