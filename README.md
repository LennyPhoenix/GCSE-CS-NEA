# Computer Science Non-Examined Assessment (GCSE)

## How to Run

### Poetry (Recommended)

- Install dependencies:
  `poetry update`
- Run:
  `poetry run python main.py`

### Pip

- Install dependencies:
  `python -m pip install pyglet==1.5.21`
- Run:
  `python main.py`

## Progress

> It should be noted that this is not meant to be a hard list for what I will work on, I will likely change the order and add more sub-tasks as I go.

- [X] Project setup, get a decent dev environment.
- [X] Application with Window, Batches and Events.
- [X] Game class with Camera and Player movement.
  - [X] Game Manager
  - [X] Physics system
    - [X] AABBs
    - [X] Physics Bodies
    - [X] Documentation
    - [X] Split up swept algorithm
  - [X] Player
    - [X] Movement
    - [X] Camera system (use groups)
    - [X] Dash
      - [X] Functionality
      - [X] Lock Velocity
    - [X] Sprite
    - [X] Animation
- [ ] Networking and player syncing.
- [ ] Combat and player UI.
- [ ] Dungeon generation.
- [ ] Enemies.
- [ ] Player classes and different weapons.
- [ ] Chest rooms and combat rooms.
- [ ] Exit room.
- [ ] Main menu and UI.

## Analysis

### Introduction

Write a graphical game that can be played from any common desktop operating system (such as Windows, OSX, and Linux).

### User Experience

- Opens into main menu.
- Play:
  - Leads to host/connect screen.
  - Hosting allows the user to create a new lobby that others can join.
  - Connect allows the user to enter an IP:Port pair and join another user's lobby.
  - Lobby screen should list players and their chosen classes, allows kicking and have a chat window.
    - Player can choose their class using a dropdown.
  - Once all players are ready, the owner may start the game.
- In Game:
  - Each player begins with a chosen class.
    - Breaker (Melee)
    - Runner (Ranger)
    - Tripper (Support)
  - Players should start in room, one exit must be present.
  - Players can attack and dash, as well as moving normally with the arrow keys or WASD.
  - Each player has 2 weapon slots and 2 item slots.
  - Selected item can be changed with num keys and scroll wheel.
  - Room is tile based with auto-tiling for smoother textures.
  - Mini-map at top right for discovered rooms.
  - Players can see other player’s locations on the map, but not their discovered rooms!
  - Objective is to find the exit room, leading to a completion.
  - Rooms along the way may contain new items (combat rooms) or new weapons (chest rooms), or may even contain a shop.
  - Enemies should drop money and health in order to reward combat, and should have different strengths and weaknesses to make multiple classes more important.
  - Exit room encounter should be more difficult than rest of the dungeon.
  - Upon exit room, new dungeon should be generated once all players enter.
  - Upon death, players may spectate other living players.
- Settings:
  - Audio volume
  - Controls
  - Networking
  - Display (for UI scaling and window size, etc)
- Info:
  - Credits and more detailed information about this task.

## Design

### Decomposition

- Application
  - The "master" object.
  - Controls:
    - The window
    - Drawing
    - Events
    - The current game state
  - Contains:
    - Main Menu
    - Lobby Menu
    - Game Manager
    - Network Manager
- Main Menu
  - Main menu user interface.
  - Controls:
    - Main menu elements
  - Contains:
    - Play Menu
    - Settings Menu
    - Info screen
- Settings Menu
  - Stores settings in a JSON file and saves to disk.
- Play Menu
  - Allows the user to host a new lobby or join an existing one.
  - Contains:
    - Text entry for username
    - Text entries for IP and PORT
    - Button to join a lobby
    - Button to host a new lobby instead
  - When the user joins or hosts a lobby, the respective method is called on the Network Manager, and control is handed over to the Lobby Menu.
- Lobby Menu
  - Allows the user to interact with the current lobby before the game begins.
  - Shows:
    - Player list and their chosen class
    - The current player can choose their own class from a menu
    - The IP:PORT pair
    - Chat window
  - Hands control over to the Game Manager once the game has started.
- Game Manager
  - Manages all the "game" processes. These include:
    - The dungeon itself
    - Entity management (Players, Enemies, Projectiles, Items, etc.)
    - Physics, likely using Pymunk
    - Win and loss conditions
    - Syncing data between clients
  - Contains:
    - Dungeon
    - Entity list
    - Players
    - Chat window
- Dungeon
  - Manages the dungeon layout.
  - Controls:
    - Dungeon generation
    - Room management
  - Contains:
    - Room data such as tiles and entities.
    - The dungeon layout
- Player
  - Controls:
    - Movement
    - Room traversal
    - Weapons and combat
    - Item usage
    - Money count
  - Contains:
    - The camera
    - Player UI (hotbar and health)
    - Inventory data
- Enemy
  - Each enemy type should have different movement and attack patterns.
  - Try to make 1 enemy for each class to help keep multiple classes important.
- Projectiles
  - Each should have a move function and lifetime value.
  - The most basic projectiles will just move forward each frame and collide with walls and entities.
- Network Manager
  - Can either create a server or connect as a client.
  - Manages all networking, including packets.
  - Host has full control, and should send dungeon and entity data to each client.
  - Clients compute their own player movement and resync with the host.

### Physics System

I have opted to avoid using a library like Pymunk for my physics system as it provides too many unnecessary tools that ultimately make the game's codebase more complex than it needs to be.

My physics system needs to do a few basic things, and nothing more:

- Allow objects to detect collisions between each other
- Resolve collisions and avoid tunneling (using swept AABBs)
- Mask out specific collision layers
  - e.g. enemies + enemy bullets do not need to collide
- Allow "move and slide" behaviour

  ![Sliding response to a swept AABB collision](https://uploads.gamedev.net/monthly_04_2013/ccs-146537-0-83526600-1366678432.png)

Something simple such as swept AABB collisions can solve this problem very easily and efficiently.

#### References

- [gamedev.net](https://www.gamedev.net/articles/programming/general-and-gameplay-programming/swept-aabb-collision-detection-and-response-r3084/)
- [amanotes.com](https://www.amanotes.com/post/using-swept-aabb-to-detect-and-process-collision)

#### Breakdown

- Object2D
  - An object in 2D space
  - X & Y - Local position
  - Parent - The parent object
  - Global X & Y - The position relative to world origin
- AABB (Axis-Aligned Bounding Box, inherits Object2D)
  - Width & Height - Bounding box extension
  - Layer and Mask - Bit fields for collision masks
  - Is Colliding AABB method: Takes AABB and checks if self and the other box overlap.
  - Is Colliding Point method: Takes coordinate pair and checks if the point is within self.
  - Get Broad Phase method: Takes a velocity pair and returns the broad phase bounding box of self moved by the given velocity.
  - Get Collision Time method: Takes a velocity and another AABB, and returns the collision time between them. (0 to 1)
  - Create Debug Rect method: Takes `*args` and `**kwargs` for a pyglet rect and generates a debug rectangle for the AABB.
  - Get Debug Rect method: Returns the current debug rect, may be `None`.
  - Update Debug Rect method: Updates the position, width, and height of the current debug rect.
- Body (Inherits AABB)
  - Move method: Gets nearest collision data and resolves by stopping at collision, returning the remaining velocity.
  - Move and Slide: Repeatedly moves until velocity is zero.
    > Check "Responses" section of the gamedev.net article for more details here.
  - Get nearest collision: Loops over each bounding box in the space given and returns the collision data for the nearest collision.
    > This will very likely need optimising, look into spatial hashing and BB tree.
- Space
  - Really just needs to be a set of AABBs.
  - When optimising, maybe turn this into a spatial hash or BB tree.
