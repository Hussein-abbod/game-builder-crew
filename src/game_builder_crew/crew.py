import os
from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class GameBuilderCrew:
    """GameBuilder crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # --- 1. DEFINE A SEPARATE LLM FOR EACH AGENT ---
        
        # CHANGED BACK TO 'gemini-flash-latest' which is safer
        self.llm_designer = LLM(
            model='gemini/gemini-2.5-flash', 
            temperature=0.7,
            api_key=os.environ.get('GOOGLE_API_KEY_DESIGNER')
        )

        self.llm_senior = LLM(
            model='gemini/gemini-2.5-flash',
            temperature=0.7,
            api_key=os.environ.get('GOOGLE_API_KEY_SENIOR')
        )

        self.llm_qa = LLM(
            model='gemini/gemini-2.5-flash',
            temperature=0.7,
            api_key=os.environ.get('GOOGLE_API_KEY_QA')
        )

        self.llm_chief = LLM(
            model='gemini/gemini-2.5-flash',
            temperature=0.7,
            api_key=os.environ.get('GOOGLE_API_KEY_CHIEF')
        )

    # --- 2. ASSIGN THE SPECIFIC LLM TO THE AGENT ---

    @agent
    def game_designer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['game_designer_agent'],
            verbose=True,
            llm=self.llm_designer  # <--- Uses Key 1
        )

    @agent
    def senior_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_engineer_agent'],
            allow_delegation=False,
            verbose=True,
            llm=self.llm_senior    # <--- Uses Key 2
        )
    
    @agent
    def qa_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_engineer_agent'],
            allow_delegation=False,
            verbose=True,
            llm=self.llm_qa        # <--- Uses Key 3
        )
    
    @agent
    def chief_qa_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['chief_qa_engineer_agent'],
            allow_delegation=True,
            verbose=True,
            llm=self.llm_chief     # <--- Uses Key 4
        )

    # --- TASKS (No changes needed here) ---

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'],
            agent=self.game_designer_agent()
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'],
            agent=self.senior_engineer_agent(),
            context=[self.design_task()] # Explicitly pass the design
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'],
            agent=self.qa_engineer_agent(),
            context=[self.code_task(), self.design_task()] # Validate code against the design
        )

    @task
    def evaluate_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_task'],
            agent=self.chief_qa_engineer_agent(),
            context=[self.review_task(), self.design_task()] # Ensure final product meets original design
        )

    # --- CREW ---

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
            max_rpm=60 # You can increase this now!
        )