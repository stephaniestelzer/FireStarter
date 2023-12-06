# FireStarter

> Version 1.0

FireStarter is a Houdini tool that aims enable artists with no Houdini experience to create high quality and customizable fire effects for their project.

Target Users are...
- Previsualization Artists who want to quickly incorporate fire into their scene
- Small Studios and Independent Creators who need fire for a shot, but don't have any VFX knowledge

### Important Info
If you want to export your simulation into Maya, you MUST use the arnold renderer for your simulation to render properly.

## How to use this tool
### Tutorials
- [Tool Set-up and Campfire UI](https://youtu.be/CZXO4NRtCm8)
- [Simulation Set-Up in Maya](https://youtu.be/b1Oej8WvssQ)

### Shelf Button Code
```python
import sys
sys.path.append("/path/to/folder/FireStarter")

from FireStarter import FireStarter

# Create an instance of the FireStarter class
fire_starter_instance = FireStarter()

# Call the run method to set up the UI and show the window
def run():
    win = FireStarter()
    win.show()
    
# Call the run method to set up the UI and show the window
def run():
    win = FireStarter()
    win.show()
    
run()
```

## Blog Posts
Throughout the development of this project, I wrote about my progress. These blogs are short and not very detailed, but they give an overview of what was accomplished each week and what I planned to get done the next week.

- [Intro](https://medium.com/@stephanie_62822/senior-project-intro-9075419a34ed)
- [Week 1](https://medium.com/@stephanie_62822/part-2-setting-up-the-hdk-and-writing-my-first-lines-of-code-237d871f8243)
- [Week 2](https://medium.com/@stephanie_62822/senior-project-part-2-qt-set-up-and-geometry-network-creation-1a07bac79fdf)
- [Week 3](https://medium.com/@stephanie_62822/senior-project-part-3-refining-requirements-goals-f92f30beb306)
- [Week 4](https://medium.com/@stephanie_62822/week-4-05fc628efb8b)
- [Week 5](https://medium.com/@stephanie_62822/senior-project-week-5-fire-spread-and-timeline-ac048abc90c3)
- [Week 6](https://medium.com/@stephanie_62822/senior-project-part-5-software-test-plan-and-spread-set-up-df286ec6d0cc)
- [Week 7](https://medium.com/@stephanie_62822/senior-project-part-6-import-exporting-files-493ff7b0dcfe)
- [Week 8](https://medium.com/@stephanie_62822/senior-project-part-7-exporting-houdini-simulations-e4ae8905c712)
- [Week 9](https://medium.com/@stephanie_62822/senior-project-part-8-entering-maya-9c2a8639c32b)
- [Week 10]()

## Checkpoint Presentations
At each stage in the development of the project, I was required to present my work.
- [Presentation 1](https://youtu.be/qnxkMSGvDfw)
- [Presentation 2](https://youtu.be/kaGZRh-jkvU)
- [Final Presentation]
