///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 22+
// Update the Quarkus version to what you want here or run jbang with
// `-Dquarkus.version=<version>` to override it.
//DEPS io.quarkus:quarkus-bom:${quarkus.version:3.14.1}@pom
//DEPS io.quarkus:quarkus-picocli
//DEPS io.quarkus:quarkus-rest-client

// langchain4j
//DEPS io.quarkiverse.langchain4j:quarkus-langchain4j-openai:RELEASE

//FILES application.properties

import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.StreamingResponseHandler;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.chat.StreamingChatLanguageModel;
import dev.langchain4j.model.output.Response;
import io.quarkus.logging.Log;
import io.vertx.core.Vertx;
import jakarta.enterprise.context.Dependent;
import jakarta.inject.Inject;
import picocli.CommandLine;
import picocli.CommandLine.Option;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

@CommandLine.Command(description = """
        An open source framework for augmenting humans using AI.

        Pick a pattern from https://github.com/danielmiessler/fabric/blob/main/patterns/ to use.
            """)
public class fabric implements Runnable {

    @Option(names = {"-p", "--pattern"}, description = "The pattern (prompt) to use", required = true)
    String pattern;

    @Option(names = {"-t", "--text"}, description = "The text to use")
    String text;

    @Option(names = {"-s", "--stream"}, description = "Stream the response")
    boolean stream;

    private final AI ai;

    public fabric(AI ai) {
        this.ai = ai;
    }

    @Inject
    Vertx vertx;

    @Override
    public void run() {
        vertx.exceptionHandler(ex -> {
            Log.info(">>> Swallowing: ", ex);
        });

        if (text == null || "-".equals(text)) {
            try (Scanner scanner = new Scanner(System.in)) {
                StringBuilder inputText = new StringBuilder();
                while (scanner.hasNextLine()) {
                    inputText.append(scanner.nextLine()).append("\n");
                }
                text = inputText.toString();
            }
        }

        String result = ai.prompt(pattern, text, stream);

        if (!stream) {
            System.out.println(result);
        }
    }

}

@Dependent
class AI {

    SystemMessage system(String text) {
        return SystemMessage.from(text);
    }

    UserMessage user(String text) {
        return UserMessage.from(text);
    }

    @Inject
    ChatLanguageModel clm;

    String prompt(String pattern, String text, boolean stream) {

        String urlPattern = "https://raw.githubusercontent.com/danielmiessler/fabric/main/patterns/%s/"
                .formatted(pattern);

        var user = downloadContent(urlPattern + "user.md");
        var system = downloadContent(urlPattern + "system.md");

        List<ChatMessage> messages = new ArrayList<>();
        if (system != null && !system.isBlank())
            messages.add(system(system));
        if (user != null && !user.isBlank())
            messages.add(user(user));
        if (text != null && !text.isBlank())
            messages.add(user(text));

        Log.info("Asking AI");
        if (stream) {
            CompletableFuture<String> future = new CompletableFuture<>();

            sclm.generate(messages, new StreamingResponseHandler<AiMessage>() {

                @Override
                public void onNext(String token) {
                    System.out.print(token);
                }

                @Override
                public void onComplete(Response<AiMessage> response) {
                    future.complete(null);
                }

                @Override
                public void onError(Throwable error) {
                    future.completeExceptionally(error);
                }
            });

            try {
                return future.get(600, TimeUnit.SECONDS);
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                throw new IllegalStateException(e);
            }

        } else {
            return clm.generate(messages).content().text();
        }

    }

    @Inject
    StreamingChatLanguageModel sclm;

    // todo: vertx or other utility method implementation
    private String downloadContent(String url) {
        String def = null;
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            return response.statusCode() == 200 ? response.body() : def;
        } catch (Exception e) {
            e.printStackTrace();
            return def;
        }
    }

}
