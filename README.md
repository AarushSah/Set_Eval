# Set_Eval
 novel benchmark for probing the visual reasoning capabilities of large language models

 ## Quickstart:
1. Clone the repository
    ```bash
    git clone https://github.com/AarushSah/Set_Eval.git
    ```
2. Install the requirements
    ```bash
    pip install -r requirements.txt
    ```
3. Add environment variables to the .env file
    ```bash
    cp .env.example .env
    ```
4. Run the evaluation for Claude-3.5 Sonnet:
    ```bash
    inspect eval evaluation.py --model anthropic/claude-3-5-sonnet-20240620
    ```
5. Run the evaluation for GPT-4o:
    ```bash
    inspect eval evaluation.py --model openai/gpt-4o
    ```
6. View Results:
    ```bash
    inspect view
    ```

### Acknowledegements:
Special thanks to [Zack Witten](https://x.com/zswitten) for the idea!