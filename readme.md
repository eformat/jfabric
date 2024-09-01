# Simple Fabric Implementation

This project is a simple implementation of the [Fabric](https://github.com/danielmiessler/fabric/) tool by Daniel Miessler. Fabric is designed to apply
pre-baked prompts and be used in a command line. 

## Usage

You can select and implement prompt patterns from the Fabric repository. Each pattern is available at:

https://github.com/danielmiessler/fabric/blob/main/patterns/


Replace `<pattern>` with the name of the pattern you wish to use.

## Configuration

OPENAI_API_KEY=YOUR_OPENAI_API_KEY
DEFAULT_MODEL=YOUR_DEFAULT_MODEL

Use your own model by setting app properties:

```absh
quarkus.langchain4j.openai.base-url=https://sno-llama31-predictor-llama-serving.apps.sno.sandbox.opentlc.com/v1
quarkus.langchain4j.openai.chat-model.model-name=/mnt/models/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf
```

## Getting Started

Install JBang, and run it with the following command:

```shell
jbang app install fabric@maxandersen/jfabric
```

Or run locally with your own model

```bash
echo <text> | jbang run fabric.java -p extract_insights -s 
```

## Examples

```shell
echo <text> | fabric -p extract_insights -s 
```

