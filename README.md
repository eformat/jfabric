# Streamlit App showcasing Fabric document summarization and generation

We combine fabric and a standalone llm to generate a services delivery document.

[Fabric](https://github.com/danielmiessler/fabric) is an open source tool by Daniel Miessler that is designed to apply
pre-baked prompts for use with a command line.

## Configuration

Use your own OpenAI compatible model by setting these env.vars

```bash
export INFERENCE_SERVER_URL=http://localhost:8080/v1
export MODEL_NAME=llama-3-8b-chat
```

Run locally using podman

```bash
podman run --rm -it -p 8501:8501 --entrypoint=bash quay.io/eformat/app3-gen
```

Build the image

```bash
make podman-build
```

## Examples

Run fabric locally

```bash
echo <text> | jbang run fabric.java -p extract_insights -s 
```

Run the streamlit application standalone

```bash
streamlit run app.py
```

## Prompts

You can select and implement prompt patterns from the Fabric repository. Each pattern is available at:

https://github.com/eformat/fabric/blob/main/patterns/
