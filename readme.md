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

## Getting Started

Install JBang, and run it with the following command:

```shell
jbang app install fabric@maxandersen/jfabric
```

## Examples

```shell
echo <text> | fabric -p extract_insights -s 
```

