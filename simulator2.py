import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Load environment variables
load_dotenv()

# Initialize the Anthropic model
model = ChatAnthropic(model="claude-3-5-sonnet-20240620")
##claude-3-haiku-20240307
##claude-3-5-sonnet-20240620
# Helper function to read XML files
def read_xml_file(filename):
    with open(filename, 'r') as file:
        return file.read()

# Load initial prompts and state
env_prompt = read_xml_file('environment_manager_prompt.xml')
npc_prompt = read_xml_file('npc_manager_prompt.xml')
initial_state = read_xml_file('state.xml')

# Environment Processor
env_processor_template = ChatPromptTemplate.from_template(
    
    "Environment Prompt: {env_prompt}\n\n"
    "Game State: {game_state}\n\n"
    
)
env_processor_chain = env_processor_template | model | StrOutputParser()

# NPC Processor
npc_processor_template = ChatPromptTemplate.from_template(
    
    "NPC Prompt: {npc_prompt}\n\n"
    "Game State: {game_state}\n\n"
    
)
npc_processor_chain = npc_processor_template | model | StrOutputParser()

# Interaction Processor
interaction_processor_template = ChatPromptTemplate.from_template(
    
    "Environment Output: {env_output}\n\n"
    "NPC Outputs: {npc_outputs}\n\n"

)
interaction_processor_chain = interaction_processor_template | model | StrOutputParser()

# Environment Updater
env_updater_template = ChatPromptTemplate.from_messages([
    ("system", read_xml_file('env_update_prompt.xml')),
    ("human", "Current Prompt: {current_prompt}\n\nInteraction Output: {interaction_output}")
])
env_updater_chain = env_updater_template | model | StrOutputParser()

# NPC Updater
npc_updater_template = ChatPromptTemplate.from_messages([
    ("system", read_xml_file('npc_update_prompt.xml')),
    ("human", "Current Prompt: {current_prompt}\n\nInteraction Output: {interaction_output}\nNPC ID: {npc_id}")
])
npc_updater_chain = npc_updater_template | model | StrOutputParser()

# State Extractor
state_extractor_template = ChatPromptTemplate.from_messages([
    ("system", read_xml_file('state_extract_prompt.xml')),
    ("human", "Interaction Output: {interaction_output}\n\nCurrent Game State: {state}")
])
state_extractor_chain = state_extractor_template | model | StrOutputParser()

# Main game turn chain
game_turn_chain = (
    RunnableParallel(
        env_output=env_processor_chain,
        npc_outputs=npc_processor_chain
    )
    | (lambda x: {"env_output": x["env_output"], "npc_outputs": x["npc_outputs"]})
    | interaction_processor_chain
    | (lambda x: {
        "interaction_output": x,
        "current_prompt": env_prompt,
        "npc_id": "npc_001",
        "state": initial_state  # Changed from 'current_state' to 'state'
    })
    | RunnableParallel(
        env_update=env_updater_chain,
        npc_updates=npc_updater_chain,
        new_state=state_extractor_chain
    )
)

# Prepare the initial input
initial_input = {
    "env_prompt": env_prompt,
    "npc_prompt": npc_prompt,
    "game_state": initial_state,
}

# Run a game turn
result = game_turn_chain.invoke(initial_input)

# Print results
print("Updated Environment Prompt:", result["env_update"])
print("Updated NPC Prompt:", result["npc_updates"])
print("New Game State:", result["new_state"])

# Save results to a Markdown file
with open("game_turn_results.md", "a") as f:
    f.write("# Game Turn Results\n\n")
    f.write("## Updated Environment Prompt\n\n")
    f.write(f"```\n{result['env_update']}\n```\n\n")
    f.write("## Updated NPC Prompt\n\n")
    f.write(f"```\n{result['npc_updates']}\n```\n\n")
    f.write("## New Game State\n\n")
    f.write(f"```\n{result['new_state']}\n```\n\n")