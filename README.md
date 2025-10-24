# Checkers Game 
**Python** based AI Checkers game featuring: 
- AI opponent powered by **Minimax algorithm**
- Three difficulty levels (Easy, Medium, Hard)
- Player vs Player game mode 
- Save and Resume Games using **SQLite** database
- Best Time Tracker per difficulty level
- Game Rules for 1st time players
- **Pygame**-based graphical interface

## 🎮 Features
### 🧠 Artificial Intelligence
- Implements **Minimax algorithm**
- Adjustable **search depth** based on difficulty
  - Easy – shallow depth, faster but weaker
  - Medium – balanced depth & performance
  - Hard – deep search, highly strategic moves
  
### 💾 Game Persistence with SQLite
- Automatically **saves ongoing games** to a local SQLite database
- Players can **resume from last save** at any time
- Stores the **best completion times** per AI difficulty

## 🚀 Installation 
### Clone Repository
```bash
git clone https://github.com/DavidDC0de/Checkers.git
cd Checkers_Game
pip install -r requirements.txt
```
### How to Run 
```bash
python main.py
```

## 📖 Tech Stack

| Componenets  | Technology |
| ------------- | ------------- |
|  Language     |  Python  |
|  Database     |  SQLite  |
|  AI Algorithm |  Minimax  |
|  GUI  |  Pygame  |

