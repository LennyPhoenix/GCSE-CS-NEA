# GCSE Computing Non-Examined Assessment

## The Task

Make a game that can be played on a desktop OS:

- Use Python + Pyglet for graphics
- Use sockets for networking
- Short and fast rounds
- Procedural dungeon generation
- Top-down gameplay

## The Game

### User Experience

- Opens into main menu.
- Play:
  - Leads to host/connect screen.
  - Hosting allows the user to create a new lobby that others can join.
  - Connect allows the user to enter an IP:Port pair and join another user's lobby.
  - Lobby screen should list players, allows kicking and have a chat window.
  - Once all players are ready, the owner may start the game.
- In Game:
  - Players should start in room, one exit must be present.
    - Each player begins with a chosen class.
      - Melee
      - Ranger
    - ADDITIONAL: Medic class that can support other players. Medium priority.
  - Players can attack and dash, each player has 2 weapon slots and 2 item slots.
  - Selected item can be changed with num keys and scroll wheel.
  - Room is tile based with auto-tiling for smoother textures.
  - Mini-map at top right for discovered rooms.
  - Players can see other player’s locations on the map, but not their discovered rooms!
  - Objective is to find the exit room, leading to a completion.
  - Rooms along the way may contain new items (combat rooms) or new weapons (chest rooms).
      - ADDITIONAL: Money and shop system. Low priority.
  - Enemies should have different strengths and weaknesses to make multiple classes more important.
  - Exit room encounter should be more difficult than rest of the dungeon.
  - Upon exit room, new dungeon should be generated once all players enter.
      - ADDITIONAL: Spectator system. High priority.
- Settings:
  - Audio volume
  - Controls
  - Networking
  - Display (UI scaling etc.)
- Info:
  - Credits and more detailed information about this task.

### Core Program Structure

- Application
  - Manages drawing, events and the window itself.
  - Should have control over the current game state.
- Main Menu
  - Holds main menu elements, along with the settings and info pages.
  - Should also contain the host/connect screen.
- Lobby Menu
  - Allows the user to interact with the current lobby before the game begins.
- Game
  - Contains world space.
  - Manages dungeon layout and tile sprites.
  - Contains the minimap UI.
  - Should control collisions and contain the player objects.
  - Basically contains and manages everything within the dungeon itself.
- Player
  - Controls player movement and camera control.
  - Manages combat.
  - Contains the player UI (hotbar and health).
- NetworkManager
  - Manages the networking connections and syncs data between clients.
  - The host should have full control over everything.
  - Each client computes everything themselves but will resync afterwards to make sure nothing weird is going on.
  - Clients send their user input and receive entity locations **only**, this helps reduce hacking.
    - This works because the only packet a hacker can replace is an input packet, which is already changeable by the user anyway.

## Checklist

> It should be noted that this is not meant to be a hard list for what I will work on, I will likely change the order and add more sub-tasks as I go.

- [X] Project setup, get a decent dev environment.
- [X] Application with Window, Batches and Events.
- [ ] Game class with Camera and Player movement.
- [ ] Networking and player syncing.
- [ ] Combat and player UI.
- [ ] Dungeon generation.
- [ ] Enemies.
- [ ] Player classes and different weapons.
- [ ] Chest rooms and combat rooms.
- [ ] Exit room.
- [ ] Main menu and UI.
