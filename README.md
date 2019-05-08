# allhands!
A basic python application for simulating warship battles in Warhammer40k Rogue Trader system.

## Current Logics

The app currently needs **two** json documents *representing a collection of ships* as input. It orders this data into two groups of opponent ships (athough it could handle multiple opponent teams), and starts the battle.
- These group of ships make shoot at each other without considering position and battery allignment.
- The ships don't move *yet*.
- In the end, when every ship in a team becomes crippled, the other team emerges as the winner.

## Features to implement
- Ships should move
    - Ships should try to approach enemy ships
    - Ships should manage speed
- Ships should manage alignment
    - Know which batteries can shoot at what
- There should be a visual representation of the fight
    - Plan to do this very simply with mathplotlib