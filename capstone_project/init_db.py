from smart_research_assistant.db.database import create_tables


def main():
    result = create_tables()
    if result.is_success():
        print("Tables created successfully")
    else:
        print(f"Failed to create tables: {result.error_message}")


if __name__ == "__main__":
    main()
