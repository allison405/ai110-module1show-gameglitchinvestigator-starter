# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
The hints for the guesses were not accurate to help with guessing the number. If the number was too high, the hint would be too low, go lower, and the if too low, the hint would be too high, go higher. It should be if the number is too high, go lower, and if the number is too low, go higher.

The blue message regarding the range was not updating according to the ranges in the different difficulty levels. I expected it to provide the actual range of numbers that are available to guess when I change the difficulty levels.

Hitting new game would not start a new game, as the whole game would stop working. It should have simply restarted the game by selecting a new random number, and then let the user type in the text box.
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
I used Claude for this project. 

For the first error, I said what was happening that was wrong and asked claude how I could fix it. To check the validity of. Its statements, I would sanity check the code myself, implement/fix it, run it in the game to view the new changes, have it write tests, and then sanity check and run the game again. 1 suggestion that was correct was that it said to flip the too low and too high statements in the try if from 37-41, so I flipped it and asked it to write tests. 1 thing that was incorrect was that it tried writing the test to match the result with the incorrect messages. Instead of go HIGHER! for example, it just wrote higher, and same idea for lower. So the test wouldn't actually work.
---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?
I first ran the game and looked at what was happening. If it was something clearly misleading to myself when I was playing without the debugger mode, I deemed it as a bug. If I had ai look at it and patch it up, then replay and it made it a better experience, I would deem it as fixed. In the case of the first error, I had claude write tests for each hint case and ran all of them. One test was if the guess was 80 and secret is 50, the outcome should show too high and tell the player to go lower.
---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

The secret number kept changing, as there is code stating that whenever a new game session starts, a random integer is generated from the selected difficult range. 
Streamlit reruns are like automatic total resets that happens everytime you type in new code. Since the system needs to let you test the new feature without the history of the old features, it will completely restart the game from the beginning. Session state is the data stored from the certain game session. Things like what number 
I did not adjust the game's secret number functionality as part of my bug fixes.  
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

I would reuse my method of finding, fixing, and testing errors through running the game, consulting claude, sanity checking and experiencing it on the game, have claude write tests, and repeating the sanity check and experience again. I believe that this allowed a thorough check through of everything, atching errors where I could instead of potentially implementing a large mistake. 
Next time, I would try to do things more in order, only fixing and testing one thing at a time. This time around, as I was trying to follow the instructions on codepath for this assignment, there were a lot of things I missed and had to come back for. (I didn't know I was only supposed to do 3 corrections. I was about to try and fix a lot of other things. I also didn't know about this reflection document, so I wasn't recording my edits or marking where I made changes)
AI generated code is actually not always just a confusing mess. In the past, I would try on chatGPT where it wouldn't really give explanations, and just give me a giant rewritten file of code to paste. However, Claude was thorough and clear with its explanations, showed where it made edits, and also thought logically about the messages(e.g. the high, low message error). I would definitely use Claude more in the future as opposed to chatGPT.

