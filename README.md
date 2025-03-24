# Do large language models understand welding?

This repository contains the code and data necessary to perform the experiments concerning LLM performance when analyzing pictures of welds.

To reproduce the experiments.

1. Clone the repository
2. Create `secrets.jsonc` file in the root of the repository with the following structure:
```
{
    "secrets": {
        "openai_key": "YOUR_OPENAI_KEY_HERE"
    }
}
```
3. Open the repo in either VSCode with the devcontainer extension, or use the `./vim_devenv/enter.sh` script to enter the development environment.
4. Run `make MODEL=gpt-4o` in the development environment to recreate GPT-4o results
5. For LLaVA-1.6, also use the make command with the correct model name `make MODEL="llava-hf/llava-v1.6-mistral-7b-hf"`. For this, you will need to run the model server script from the `./remote_scripts` directory, and point the config file at the machine where the server is running.
6. The results will be created in the `./results` directory
