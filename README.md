# Page-Turner
A TKinter programme that lets musicians or other users turn pdf pages or jump to others with voice commands.
Requirements - 
python 3.12
  Python libraries - 
  fitz
  tkinter
  PIL
  sys
  speech_recognition
  difflib
  copy
How to use - 
Run the file "Page turner.py" with your microphone turned on. The current version of the programme uses the 0 slot microphone by default.
Use the commands "turn right", "go right", "next", "next page", "go forward", "forward" to go to the next page.
Use the commands "turn left", "go left", "previous", "previous page", "go back", "back" to go to the previous page.
Use the commands "Stop" or "Quit" to end the programme.
Use either "Go to", "Go to page" followed by a number or simply the page number itself to go to that page specifically.
You can also use the "Previous page" and "Next page" buttons at the bottom of the TKinter window to manually go right or left.
Enter a number into the text field and then click "Go to selected page" to go straight there.
Click the "File" button at the top-left to either exit or select a new file for reading.
Currently there is a bug where although previously loaded files are stored by the programme and appear in the menu, they cannot actually be loaded again or update the UI.
