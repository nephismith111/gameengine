# Coding Conventions

## Technology Stack
- **Backend**: Python, Django (with Django Channels)
- **Frontend**: Vanilla JavaScript with jQuery (no React/JSX)
- **Bundling**: Webpack (via Django Webpack integration)
- **Templating**: Django Templates (not Jinja)
- **Database**: PostgreSQL for both domain data and user management via Django ORM
- **Channel Communication**: Redis (used by Django Channels for group communication and reliable pub/sub)
- **Testing**: Django unittest, PyVCR
- **API Documentation**: OpenAPI (`openapi.yaml`) — this is the **source of truth** for the interface between the front end and the backend
- **WebSocket Documentation**: AsyncAPI (`asyncapi.yaml`) — defines the format of messages from the server to the client
- **Assets**: Use CDN-hosted libraries when possible to simplify asset management
- **Development Environment**: Developed in Docker using `docker-compose` with a shared network. `credentials.py` provides hostnames in case services are moved outside of `docker-compose`

## Project Structure
- Project root contains:
  - `Dockerfile`, `docker-compose.yml`, `package.json`, `node_modules`, `webpack.config.js`
- Django project lives under `./project/<project-name>/`
  - Example: `./project/gameengine/` contains all Django apps, including the core app `gameengine`
- **Django App Naming**:
  - App names must be one word: no underscores, dashes, periods, or separators
  - Aim for no more than two concatenated words (e.g., `towercontrol`, `userauth`)
- All URLs must be documented in `<project-root>/openapi.yaml`
- URL Types:
  - API URLs (defined in `v1_urls.py`, or split into `v1_urls_<name>.py` as needed)
  - HTTP URLs (defined in `urls.py`)
- Each Django app should have its own API namespace: `/<app>/v1/<resource>` (not `/v1/<app>/<resource>`) 
- JavaScript is bundled with Webpack and included via Django template tags
  - Always remember to load the Webpack tag before rendering the bundle:
    ```django
    {% load render_bundle from webpack_loader %}
    {% render_bundle 'ConnectorListApp' %}
    ```
- All frontend assets are managed through Django Webpack and should not be placed in `/static` folders manually
- Static and Webpack files:
  - Each app has a `<django_app>/static/<django_app>` folder
  - App-specific styles go in `<django_app>/static/<django_app>/css/styles.css`
  - Webpack JS code goes in `<django_app>/webpack/`
    - The entrypoint should be named `<django_app>_root.js`
    - This name is used in `webpack.config.js`
  - The only exception is the webpack_bundles directory which can be in the project's static directory
- Templates:
  - Templates live in `templates/<django_app>/`
  - Each app’s main HTML file (e.g., `index.html`) should extend `core/templates/base.html`
  - The core app owns and serves the shared CSS and layout logic
- The core Django app (named after the project) contains:
  - Shared base templates and assets
  - Shared logic and configuration
  - `credentials.py`: All external access details (usernames, passwords, hosts, ports)
  - `project_settings.py`: Project-specific configuration (kept out of `settings.py`)
  - `environment_settings.py`: Metadata about environment such as hostnames and deployment context
  - User authentication and login functionality (using Django ORM)
- Each Django app must have:
  - `interfaces.py`: Exposes functions/data needed by other apps. Cross-app imports must go through here
  - `models.py`: Defines domain-specific Django models (e.g., Tower). These describe and standardize shared app assets
  - `exceptions.py`: Defines custom exceptions specific to the app
  - `managers.py`: Contains custom model managers and querysets for complex database operations
- Django views MUST be minimal: unpack variables, call a logic function, repack, and return response
  - Django-specific objects (like requests) should not be passed into logic functions
  - Logic must live in `./src/<self_documenting_name>.py`, e.g., logic for tower placement goes in `./src/towers.py`

## Core Principles
- **Simplicity First**: Keep code as simple as possible, avoiding unnecessary complexity
- **Self-Documenting Code**: Use meaningful names that reveal intent
- **Function Design**: Small, focused functions doing one thing well
- **Modularity**: Refactor files exceeding 500-1000 lines
- **Readability**: Code should be easy to understand at a glance
- **Security**: Implement best practices to protect against vulnerabilities

## Universal Patterns
- **Single Exit Point**: One return statement at the end of each function
- **Function Size**: Prefer smaller, more focused functions
- **Logging**: Include logging for user actions to aid troubleshooting and auditing
- **Modularity**: Break files larger than 500 lines into multiple files
- **Configuration**: Store configuration in dedicated files or as globals at the top of files when it improves readability
- **Typing**: Use light typing — avoid full mypy rigor, but annotate for clarity and consistency
- **String Formatting**: Use f-strings; avoid concatenation or logic in Django templates — resolve variables before passing

## Communication Conventions
- **User Actions**: Sent to the server using jQuery AJAX calls
- **API Contract**: The `openapi.yaml` defines the full server-side API contract. The server MUST fully implement this. The front end MUST use this as the only reference to fetch and work with data.
- **WebSocket Contract**: Defined in `asyncapi.yaml`, documents all server-to-client messages. WebSocket communication is **one-way** from server to browser only.
- **API Behavior**: An API call from the client may result in:
  - A database write
  - A Redis channel publish (via Django Channels)
  - Or both
- **State Updates**: Server-side changes persist to PostgreSQL
- **Realtime Feedback**: Sent from server to client via plain WebSocket
- **Channel Group Naming**: Use functions from `channel_groups.py` to generate consistent channel group names
  - Never hardcode channel group names in WebSocket consumers or messaging functions
  - All group name generation should be centralized in the `channel_groups.py` file
- **Rendering Philosophy**: Prefer frontend rendering over server-side rendering
  - The server provides only the base HTML page
  - **No data should be preloaded into the HTML** — all data must be fetched asynchronously after page load
  - JavaScript updates only the necessary DOM elements, minimizing full-page refreshes

## Python/Django Guidelines
- **Views**: 
  - Always use class-based Django views, not function-based views
  - For API views, use Django REST Framework's APIView or generic views
  - Apply CSRF exemption to API views using `@method_decorator(csrf_exempt, name='dispatch')`
- **API Separation**: Keep HTML-serving views separate from JSON API views
  - Use `v1_urls.py` and `v1_views.py`, or `v1_urls_<name>.py` and `v1_views_<name>.py` for large APIs
  - All API URLs should have `v1/` prefix for extensibility
- **URL Routing**: Prefer Django `re_path` over `path`
- **Configuration**: Import variables from `credentials.py` rather than requesting them from the browser
- **Code Organization**: Keep the django views tiny: unpack variables, call a function to do logic `<app>/src/<logic>.py`, then repack the results and send it off. Functions should be TINY.
- **Python Types**: Use typing to clarify intent, especially on public interfaces, without full static enforcement

## Python Testing
- Use django unittest with pyvcr. Record interactions in `<app>/tests/fixtures/vcr_cassetts/<file>.yaml`
- Write a test file in the `<app>/tests` for each major function of the API
- **Testing Theory**: Tests are a source of truth and prove that the `openapi.yaml` is true. Proving this spec is the goal, not testing every function. I don't care how it works, just that it follows the contract (this allows the inside to be refactored and confidence to be given that the API still behaves correctly for clients).
- **Feature Tracking**: All features must be documented in `features.md` at the project root. This file helps with designing and maintaining tests by tracking which features have been tested and which haven't.

## JavaScript Guidelines
- **Separation of Concerns**: 
  - DOM interaction and event handling in JS files
  - API interactions via jQuery AJAX
- **Entry Point**: Each page must define its entrypoint JS file for Webpack
  - Root files should be small and focused on initialization
  - Split functionality into separate modules for better maintainability
  - Root files should primarily handle document ready functions and module initialization
- **Resource Management**: 
  - Call API endpoints for data rather than preloading in HTML
  - Use CDN-hosted libraries whenever feasible
- **URL Management**: 
  - Collect URLs in a single JS file per app as an importable object
  - No hardcoded URL fragments in JavaScript files
- **Code Location**: 
  - JavaScript should reside in Webpack-managed folders
  - Remove unnecessary `<static>` tags from HTML templates
- **Prohibited Practices**:
  - Do NOT use the `async` keyword
  - Avoid direct DOM manipulation with `document.getElementByXXX` unless absolutely necessary
- **Javascript Nuances**:
  - Prefer using callbacks and `.bind(this)` instead of Promises for better control of `this`
  - Deconstruct needed variables at the top of each function to clarify data sources and reduce verbosity
- **Module Organization**:
  - Split large JavaScript files into focused modules with clear responsibilities
  - Use ES6 import/export syntax for module dependencies
  - Keep modules under 300 lines of code when possible

## Webpack Configuration
- JavaScript must go inside Webpack folders for each Django app
- Webpack code belongs in `<django_app>/webpack/`
  - Use a `<django_app>_root.js` file as the entry point
  - Register these entry points in `webpack.config.js`
- Add bundle references using Django template tags in the appropriate HTML templates
  - Always load the render bundle tag:
    ```django
    {% load render_bundle from webpack_loader %}
    {% render_bundle 'YourBundleName' %}
    ```

## Docker Development
- All Django commands should be run inside the Docker container
- To run migrations:
  ```bash
  docker-compose exec web python project/gameengine/manage.py migrate
  ```
- To create migrations:
  ```bash
  docker-compose exec web python project/gameengine/manage.py makemigrations
  ```
- To create a superuser:
  ```bash
  docker-compose exec web python project/gameengine/manage.py createsuperuser
  ```
- To run the Django shell:
  ```bash
  docker-compose exec web python project/gameengine/manage.py shell
  ```

## Game Flow and Architecture

### Welcome Page
- The welcome page displays:
  - A grid of game tiles (each representing a game type)
  - A horizontal divider
  - A table of game instances (pending, ongoing, or ended)
- Game instance table features:
  - Sorted by status (pending at top, ongoing next, ended at bottom)
  - Within each status group, sorted by started_datetime
  - Columns: Game Type, Instance Name, Status, Players (current/max), Player Names, Actions

### Game Joining Process
- Users can join existing games if:
  - The game status is "pending"
  - Current player count < max_players
- To create a new game:
  1. User clicks on a game tile
  2. User is prompted to enter a game instance name
  3. System creates a new game instance with:
     - Status: "pending"
     - The creating user added to joined_users
     - Game settings copied from game type defaults
  4. User is navigated to the waiting room

### Waiting Room
- Game-specific waiting room shows:
  - Game instance name
  - List of joined players
  - Start game button (visible only to the creator)
- When the game starts:
  - Status changes to "ongoing"
  - started_datetime is set
  - All players are navigated to the game page

### Game Models
1. **GameType Model**:
   - name: Name of the game type (e.g., "TowerDefense")
   - image_url: URL to the tile image
   - max_players: Maximum number of players allowed
   - default_settings: JSONField containing game-specific default settings
   - description: Text description of the game

2. **GameInstance Model**:
   - id: UUID primary key
   - game_type: ForeignKey to GameType
   - instance_name: User-defined name for this game instance
   - status: Choice field ("pending", "ongoing", "ended")
   - started_datetime: When the game started (null if pending)
   - ended_datetime: When the game ended (null if pending/ongoing)
   - game_data: JSONField containing:
     - joined_users: List of dicts with user IDs and usernames
     - game_settings: Copy of settings from the game type, possibly modified

### Data Flow
- Game types and their default settings are defined in GAMES.md
- A migration will create the initial GameType entries (idempotently)
- Game instances are created when users start new games
- Game state is managed through the game_data JSONField

# Coding Conventions

## Technology Stack
- **Backend**: Python, Django (with Django Channels)
- **Frontend**: Vanilla JavaScript with jQuery (no React/JSX)
- **Bundling**: Webpack (via Django Webpack integration)
- **Templating**: Django Templates (not Jinja)
- **Database**: PostgreSQL for both domain data and user management via Django ORM
- **Channel Communication**: Redis (used by Django Channels for group communication and reliable pub/sub)
- **Testing**: Django unittest, PyVCR
- **API Documentation**: OpenAPI (`openapi.yaml`) — this is the **source of truth** for the interface between the front end and the backend
- **WebSocket Documentation**: AsyncAPI (`asyncapi.yaml`) — defines the format of messages from the server to the client
- **Assets**: Use CDN-hosted libraries when possible to simplify asset management
- **Development Environment**: Developed in Docker using `docker-compose` with a shared network. `credentials.py` provides hostnames in case services are moved outside of `docker-compose`
- **Python Environment**: Uses the global Python interpreter in Docker containers (no virtual environments) as the container itself provides isolation

## Project Structure
- Project root contains:
  - `Dockerfile`, `docker-compose.yml`, `package.json`, `node_modules`, `webpack.config.js`
- Django project lives under `./project/<project-name>/`
  - Example: `./project/gameengine/` contains all Django apps, including the core app `gameengine`
- **Django App Naming**:
  - App names must be one word: no underscores, dashes, periods, or separators
  - Aim for no more than two concatenated words (e.g., `towercontrol`, `userauth`)
- All URLs must be documented in `<project-root>/openapi.yaml`
- URL Types:
  - API URLs (defined in `v1_urls.py`, or split into `v1_urls_<name>.py` as needed)
  - HTTP URLs (defined in `urls.py`)
- Each Django app should have its own API namespace: `/<app>/v1/<resource>` (not `/v1/<app>/<resource>`) 
- JavaScript is bundled with Webpack and included via Django template tags
  - Always remember to load the Webpack tag before rendering the bundle:
    ```django
    {% load render_bundle from webpack_loader %}
    {% render_bundle 'ConnectorListApp' %}
    ```
- All frontend assets are managed through Django Webpack and should not be placed in `/static` folders manually
- Static and Webpack files:
  - Each app has a `<django_app>/static/<django_app>` folder
  - App-specific styles go in `<django_app>/static/<django_app>/css/styles.css`
  - Webpack JS code goes in `<django_app>/webpack/`
    - The entrypoint should be named `<django_app>_root.js`
    - This name is used in `webpack.config.js`
  - The only exception is the webpack_bundles directory which can be in the project's static directory
- Templates:
  - Templates live in `templates/<django_app>/`
  - Each app's main HTML file (e.g., `index.html`) should extend `core/templates/base.html`
  - The core app owns and serves the shared CSS and layout logic
- The core Django app (named after the project) contains:
  - Shared base templates and assets
  - Shared logic and configuration
  - `credentials.py`: All external access details (usernames, passwords, hosts, ports)
  - `project_settings.py`: Project-specific configuration (kept out of `settings.py`)
  - `environment_settings.py`: Metadata about environment such as hostnames and deployment context
  - User authentication and login functionality (using Django ORM)
- Each Django app must have:
  - `interfaces.py`: Exposes functions/data needed by other apps. Cross-app imports must go through here
  - `models.py`: Defines domain-specific Django models (e.g., Tower). These describe and standardize shared app assets
  - `exceptions.py`: Defines custom exceptions specific to the app
  - `managers.py`: Contains custom model managers and querysets for complex database operations
- Django views MUST be minimal: unpack variables, call a logic function, repack, and return response
  - Django-specific objects (like requests) should not be passed into logic functions
  - Logic must live in `./src/<self_documenting_name>.py`, e.g., logic for tower placement goes in `./src/towers.py`

## Core Principles
- **Simplicity First**: Keep code as simple as possible, avoiding unnecessary complexity
- **Self-Documenting Code**: Use meaningful names that reveal intent
- **Function Design**: Small, focused functions doing one thing well
- **Modularity**: Refactor files exceeding 500-1000 lines
- **Readability**: Code should be easy to understand at a glance
- **Security**: Implement best practices to protect against vulnerabilities

## Universal Patterns
- **Single Exit Point**: One return statement at the end of each function
- **Function Size**: Prefer smaller, more focused functions
- **Logging**: Include logging for user actions to aid troubleshooting and auditing
- **Modularity**: Break files larger than 500 lines into multiple files
- **Configuration**: Store configuration in dedicated files or as globals at the top of files when it improves readability
- **Typing**: Use light typing — avoid full mypy rigor, but annotate for clarity and consistency
- **String Formatting**: Use f-strings; avoid concatenation or logic in Django templates — resolve variables before passing

## Communication Conventions
- **User Actions**: Sent to the server using jQuery AJAX calls
- **API Contract**: The `openapi.yaml` defines the full server-side API contract. The server MUST fully implement this. The front end MUST use this as the only reference to fetch and work with data.
- **WebSocket Contract**: Defined in `asyncapi.yaml`, documents all server-to-client messages. WebSocket communication is **one-way** from server to browser only.
- **API Behavior**: An API call from the client may result in:
  - A database write
  - A Redis channel publish (via Django Channels)
  - Or both
- **State Updates**: Server-side changes persist to PostgreSQL
- **Realtime Feedback**: Sent from server to client via plain WebSocket
- **Rendering Philosophy**: Prefer frontend rendering over server-side rendering
  - The server provides only the base HTML page
  - **No data should be preloaded into the HTML** — all data must be fetched asynchronously after page load
  - JavaScript updates only the necessary DOM elements, minimizing full-page refreshes

## Python/Django Guidelines
- **Views**: Prefer class-based Django views over function-based
- **API Separation**: Keep HTML-serving views separate from JSON API views
  - Use `v1_urls.py` and `v1_views.py`, or `v1_urls_<name>.py` and `v1_views_<name>.py` for large APIs
  - All API URLs should have `v1/` prefix for extensibility
- **URL Routing**: Prefer Django `re_path` over `path`
- **Configuration**: Import variables from `credentials.py` rather than requesting them from the browser
- **Code Organization**: Keep the django views tiny: unpack variables, call a function to do logic `<app>/src/<logic>.py`, then repack the results and send it off. Functions should be TINY.
- **Python Types**: Use typing to clarify intent, especially on public interfaces, without full static enforcement

## Python Testing
- Use django unittest with pyvcr. Record interactions in `<app>/tests/fixtures/vcr_cassetts/<file>.yaml`
- Write a test file in the `<app>/tests` for each major function of the API
- **Testing Theory**: Tests are a source of truth and prove that the `openapi.yaml` is true. Proving this spec is the goal, not testing every function. I don't care how it works, just that it follows the contract (this allows the inside to be refactored and confidence to be given that the API still behaves correctly for clients).

## JavaScript Guidelines
- **Separation of Concerns**: 
  - DOM interaction and event handling in JS files
  - API interactions via jQuery AJAX
- **Entry Point**: Each page must define its entrypoint JS file for Webpack
- **Resource Management**: 
  - Call API endpoints for data rather than preloading in HTML
  - Use CDN-hosted libraries whenever feasible
- **URL Management**: 
  - Collect URLs in a single JS file per app as an importable object
  - No hardcoded URL fragments in JavaScript files
- **Code Location**: 
  - JavaScript should reside in Webpack-managed folders
  - Remove unnecessary `<static>` tags from HTML templates
- **Prohibited Practices**:
  - Do NOT use the `async` keyword
  - Avoid direct DOM manipulation with `document.getElementByXXX` unless absolutely necessary
- **Javascript Nuances**:
  - Prefer using callbacks and `.bind(this)` instead of Promises for better control of `this`
  - Deconstruct needed variables at the top of each function to clarify data sources and reduce verbosity

## Webpack Configuration
- JavaScript must go inside Webpack folders for each Django app
- Webpack code belongs in `<django_app>/webpack/`
  - Use a `<django_app>_root.js` file as the entry point
  - Register these entry points in `webpack.config.js`
- Add bundle references using Django template tags in the appropriate HTML templates
  - Always load the render bundle tag:
    ```django
    {% load render_bundle from webpack_loader %}
    {% render_bundle 'YourBundleName' %}
    ```
