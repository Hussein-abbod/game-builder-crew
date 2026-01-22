import gradio as gr
from game_builder_crew.crew import GameBuilderCrew
from dotenv import load_dotenv  # <--- ADD THIS
load_dotenv()

# --- The Logic Function ---
def generate_game_code(custom_prompt):
    """
    Takes the user's custom text and runs the Crew.
    """
    if not custom_prompt:
        return "# Please enter a game idea first!"

    inputs = {
        'game': custom_prompt
    }

    try:
        # The 'design_task' will now run first to refine this prompt!
        result = GameBuilderCrew().crew().kickoff(inputs=inputs)
        return str(result)
    except Exception as e:
        return f"# Error generating code:\n# {str(e)}\n# (Check your API Key)"

# --- The Gradio Interface ---
def launch_app():
    with gr.Blocks(title="AI Game Generator", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("# 🎮 Custom AI Game Creator")
        gr.Markdown("Describe any game idea, and our AI Design Team will build it for you.")
        
        with gr.Row():
            with gr.Column(scale=1):
                # CHANGED: Textbox instead of Dropdown
                game_input = gr.Textbox(
                    label="Describe your game idea", 
                    placeholder="Example: A game where a cat catches falling fish. Use arrow keys to move. Score goes up for every fish.",
                    lines=5
                )
                
                generate_btn = gr.Button("🚀 Build My Game", variant="primary")
                
                gr.Markdown("### How it works:")
                gr.Markdown("1. **Game Designer Agent** refines your idea into a spec.\n2. **Senior Engineer** writes the code.\n3. **QA Team** checks for bugs.")

            with gr.Column(scale=2):
                code_output = gr.Code(
                    language="python", 
                    label="Generated Python Code", 
                    lines=20, 
                    interactive=False
                )

        generate_btn.click(
            fn=generate_game_code, 
            inputs=[game_input], 
            outputs=[code_output]
        )

    demo.launch(share=True)

if __name__ == "__main__":
    launch_app()