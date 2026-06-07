This is a simple model to understand the language models in depth.

Using mojo isn't the right choice here, but for some fun. I incorporate the following steps for the project integration.

1. LLM call: Interact with mojo and openrouter free models. Use `request` library from python for this.
2. Two call setup for integration and response cycle of a simple loop.

Run:

```
pixi add requests 
pixi add "python<=3.10" # due to some error the working version is >3.11
git submodule add https://github.com/databooth/mojo-dotenv vendor/mojo-dotenv # working solution for reading .env
```

Fed up with the environment loading in mojo. The standard library is outdated, and the working submodule is also having an error due to def keyword. Maybe a pull request. 

Until then a naive implemenation of the value passing is implemented in `dotenv.py`. 
