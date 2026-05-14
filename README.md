# badmintellect

badmintellect is a simple sports reservation website themed around badminton. badmintellect is built with Flask and uses uv for dependency management.

## Features

- Simple account system with session handling and basic security measures.
- Viewing, creating and editing reservations.
- Searching for reservations with multiple filters.
- Enrolling in reservations and commenting.

## Development

1. Clone the repository.

```bash
git clone https://github.com/hatonlee/badmintellect.git
```

2. Run the initialization script.

```bash
uv run init
```

3. Launch the development server.

```bash
uv run flask --app src/badmintellect/app.py run
```
