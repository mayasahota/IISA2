# IISA2
A2 Submission for IIS Module
Word Count: 888 words

# Project status
I have developed a web app prototype of my designed text simplification system for people with Dyslexia. 

Implemented:
- Accessibility settings
- Choice of text box, OCR or file upload input
- Original text remains on the screen and is editable
- Progressive simplification loop (can progressively click to simplify, though actual simplification is simulated)
- Undo simplification to one level back (can click continually)
- Information about how the system works and data sharing info for user (when sending to human reviewer)

Simulated:
- OCR and file upload (sample text is used to simulate each input)
- Text simplification (hardcoded text comprehension levels are used instead of progressive simplification)
- Independent AI checker (confidence is based on how much of the original word count is kept rather than an independent AI deciding maximum simplification level. This is not a reliable way of measuring meaning retention, but simulates how the system would respond)
- Flag incorrect (the system simulates a new simplification being generated)
- Human reviewer (a 4 second timer simulates the time of a human checking and verifying the meaning of text)

What remains unfinished: 
- Implementation of human verification system
- Elements simulated rather than implemented

# Technology stack
I developed my prototype in VS Code and used Git and GitHub for version control. The frontend was developed using HTML with CSS and JavaScript. The backend was built in Python using http.server, json and re. I used this tech stack because I was familiar with it, as it followed a similar approach to the simulated system built in week 4. To develop my prototype Claude Sonnet 5.5 with the coding, as I had access to the model and since it has strong coding skills it felt suitable.

For a future iteration with OCR and actual LLM implementation (simplification and checker), a system that can provide each of these would need to be selected, but is out of scope for this prototype.

# Running or inspecting the work
By running the following commands, the system can be run on local host:

git clone https://github.com/mayasahota/IISA2.git
cd IISA2
python app.py

Then open http://localhost:8000

From the home page, you can select the input method and follow the prompts to use the system's features. Other than having Python 3 installed, there is no additional software, API keys or setup required.

# Development record 
I started by asking the LLM to make the frontend of the app (Commit 91d0997c017732125f2a7832e53286d168161f47). I drew a mockup of what the app should look like and provided it to the LLM so I could ensure the app looked the way I wanted before adding any functionality. 

I then went through the features one by one, manually checking the code and its output in the browser before committing:
1. Simplification loop and the limit to the loop (when meaning is lost) (Commit 504cecf2a79767699bb0b986047fdf5e2c1eb62f)
2. Accessibility (Commit d11515f081445a144c29615c94097d2463b37661)
3. Text input method (at this point I decided it would be best to have the actual simplification on a different page to reduce the amount of content on the page at once to reduce cognitive overload) (Commit 462fd6f9fbe8ea7ef38f9d1ba06dd26c5205f5a8)
4. Undo simplification level (Commit 7cad6dab468691b092f53f1c79d510cc656208a5)
5. Flag as incorrect (Commit 3632eadb188db4e40805bc11a3792791161f6faf)
6. Request human verification (Commit 253f33f51a907955082207780fd8ecc6304cb69e)

As I was going through, I made tweaks to the AI generated content to make it more user-friendly, or more aligned to my design eg. changing from decimals to percentages having separate simulated texts for each input method (commit 0d132ec2fc05dd20b6fbdeb55b9835644a8cab1a, e566dfcbf57e805aeb9c1a2d1fc0bc666ae2c836). Going through one feature at a time helped me to see any changes that needed to be made rather than having to sift through lots of code.

Claude added a 'Back to Original' button, I chose not to include this in my system. Although the feature may be useful, the functionality already exists via continually selecting the undo button. It was important that I kept the interface simple and easy to use and an extra button may cause cognitive overload.

I also added an information page, with the assistance of AI, so the user is clear on what the system is and how it works.

# AI assistance
I did not use AI for the development of my design report. I made use of the papers that I had read for A1 and my knowledge of designing IIS that I got from the lectures. I also did not use AI for my storyboards or architecture diagram as I felt that drawing out my own understanding of the system helped me with knowing how I wanted it to be developed. Also, I was able to convey the intended designs when drawing and describing them myself rather than an LLM interpretation of what the system needed. 

Once I had finished the report, I gave it to ChatGPT 5.6 to see if there were any obvious issues with it and made a few small changes, such as some clarity issues in my design rationale section, but did not use it to write content.

I used Anthropic Claude Sonnet 5.5 to help me with the development of my prototype. I first provided it with my design document and my wireframe of the frontend, then went through feature by feature to develop the prototype. I checked the code by reading it, then ran each part of the code to ensure it was what I expected and needed; I adjusted my prompts and the code wherever needed. 

# Additional files
I made a folder in the GitHub repo called 'Additional Files', which stores my frontend mockup drawing /Additional Files/frontendMockup.jpeg
