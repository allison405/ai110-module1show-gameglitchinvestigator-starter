# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [ ] This game is an interactive number-guessing game. You can choose your own difficulty level, make attempts at guessing the secret number, and get a finalized score! Replay as many times as you want, but you only get a certain number of tries each round, so you have to make intuitive guesses. Toggle on or off the hints, or change your difficulty level to align with your game-playing needs.
- [ ] Bugs I found were in the hints given, the initial message displayed, and the broken new game function. The hints were misleading the user in getting towards the right number. The initial message didn't provide the correct range of numbers to guess from. Attempting to start a new game by hitting the corresponding button would result in the entire game not working anymore.
- [ ] I adjusted the game by patching the bugs listed above, aligning them more to a normal user experience, fixed the new game so that users could continue playing more rounds, and also moved some code from the app.py file over to logic_utils.py.

## 📸 Demo

- [ ] 

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
