```text
Implement the caching concept found in the documentation into the project.
```

# Java files - ref/what2eat

## `src/main/java/de/schneider21/what2eat/Application.java`

```java
package de.schneider21.what2eat;

import de.schneider21.what2eat.framework.HttpServer;
import de.schneider21.what2eat.meal.api.MealController;
import fi.iki.elonen.NanoHTTPD;

import java.io.IOException;

public class Application {

    public static void main(String[] args) throws IOException {
        final HttpServer httpServer = new HttpServer(8080);
        httpServer.registerRestController(new MealController());
        httpServer.start(NanoHTTPD.SOCKET_READ_TIMEOUT, false);
        System.out.println("Application: Server running on localhost:8080/...");
    }
}

```

## `src/main/java/de/schneider21/what2eat/ServiceFactory.java`

```java
package de.schneider21.what2eat;

import de.schneider21.what2eat.meal.business.*;

/**
 * Service Factory. Central entry point for getting the service implementations.
 * Modeled as singleton. Use {@link ServiceFactory#getInstance()} to access the (single) instance.
 */
public class ServiceFactory {

    private static volatile ServiceFactory INSTANCE;

    public static ServiceFactory getInstance() {
        // double check idiom
        if (INSTANCE == null) {
            synchronized (ServiceFactory.class) {
                if (INSTANCE == null) {
                    INSTANCE = new ServiceFactory();
                }
            }
        }
        return INSTANCE;
    }

    private IMenuService menuService;
    private IMealService mealService;
    private IWeatherService weatherService;

    private ServiceFactory() {
        menuService = new MensaKlService();
        weatherService = new WeatherBitService();
        mealService = new MealService(menuService, weatherService);
    }


    public IMealService getMealService() {
        return mealService;
    }

    public IMenuService getMenuService() {
        return menuService;
    }

    public IWeatherService getWeatherService() {
        return weatherService;
    }
}

```

## `src/main/java/de/schneider21/what2eat/framework/HttpServer.java`

```java
package de.schneider21.what2eat.framework;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import fi.iki.elonen.NanoHTTPD;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

public class HttpServer extends NanoHTTPD {

    public HttpServer(int port) {
        super(port);
    }

    private final ObjectWriter objectWriter = new ObjectMapper().writerWithDefaultPrettyPrinter();

    private final List<RestController> restControllers = new ArrayList<>();

    public void registerRestController(RestController restController) {
        restControllers.add(restController);
    }

    @Override
    public Response serve(IHTTPSession session) {

        final String path = session.getUri();
        System.out.printf("HttpServer: Incoming %s request for %s with params %s\n", session.getMethod(), path,
                session.getParms());

        if (session.getMethod() == Method.GET) {
            for (RestController restController : restControllers) {
                for (Map.Entry<String, Function<RestController.IRequestParameters, Object>> httpGetMapping :
                        restController.httpGetMappings().entrySet()) {
                    final String pathExpression = httpGetMapping.getKey();
                    if (path.matches(pathExpression)) {
                        try {
                            final Object returnObject =
                                    httpGetMapping.getValue().apply(new RestController.IRequestParameters() {
                                        @Override
                                        public String getQueryParameter(String parameterName) {
                                            return session.getParms().get(parameterName);
                                        }

                                        @Override
                                        public String getPath() {
                                            return path;
                                        }
                                    });

                            return newFixedLengthResponse(Response.Status.OK, "application/json",
                                    objectWriter.writeValueAsString(returnObject));
                        } catch (Exception e) {
                            return newFixedLengthResponse(Response.Status.INTERNAL_ERROR, NanoHTTPD.MIME_PLAINTEXT,
                                    "ERROR: " + e.getMessage());
                        }
                    }
                }
            }
        }

        // ... could be extended for other methods, e.g. POST, PUT, DELETE

        return newFixedLengthResponse(Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, "Path/Method not supported");

    }
}

```

## `src/main/java/de/schneider21/what2eat/framework/RestController.java`

```java
package de.schneider21.what2eat.framework;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

public abstract class RestController {

    public interface IRequestParameters {
        String getQueryParameter(String parameterName);

        String getPath();
    }

    private final Map<String, Function<IRequestParameters, Object>> getMappings = new HashMap<>();

    /**
     * Registers a path pattern to be handled by one of the controllers functions
     *
     * @param pathPattern is matched as regular expression
     * @param handler     the function to be called. The returned object is serialized as JSON
     */
    protected void addHttpGetMapping(String pathPattern, Function<IRequestParameters, Object> handler) {
        getMappings.put(pathPattern, handler);
    }

    public Map<String, Function<IRequestParameters, Object>> httpGetMappings() {
        return getMappings;
    }
}

```

## `src/main/java/de/schneider21/what2eat/meal/api/MealController.java`

```java
package de.schneider21.what2eat.meal.api;

import de.schneider21.what2eat.ServiceFactory;
import de.schneider21.what2eat.framework.RestController;
import de.schneider21.what2eat.meal.business.IMealService;
import de.schneider21.what2eat.meal.data.BasicMeal;
import de.schneider21.what2eat.meal.data.ExtendedMeal;

import java.util.List;

public class MealController extends RestController {

    public MealController() {
        super();
        addHttpGetMapping("/meal", this::getMeals);
        addHttpGetMapping("/meal/.*", this::getMeal);
    }

    public List<BasicMeal> getMeals(IRequestParameters parameters) {
        final IMealService mealService = ServiceFactory.getInstance().getMealService();
        final List<BasicMeal> meals = mealService.getAllAvailableMeals();

        return meals;
    }

    public ExtendedMeal getMeal(IRequestParameters parameters) {
        final String dateFromPath = parameters.getPath().substring("/meal/".length());

        final IMealService mealService = ServiceFactory.getInstance().getMealService();
        final ExtendedMeal meal = mealService.getExtendedMealForDate(dateFromPath);

        return meal;
    }

}

```

## `src/main/java/de/schneider21/what2eat/meal/business/IMealService.java`

```java
package de.schneider21.what2eat.meal.business;

import de.schneider21.what2eat.meal.data.BasicMeal;
import de.schneider21.what2eat.meal.data.ExtendedMeal;

import java.util.List;

public interface IMealService {

    List<BasicMeal> getAllAvailableMeals();

    ExtendedMeal getExtendedMealForDate(String dateString);

    int calculateColdBowlProbabilityInPercent(Double temperature);
}

```

## `src/main/java/de/schneider21/what2eat/meal/business/IMenuService.java`

```java
package de.schneider21.what2eat.meal.business;

import de.schneider21.what2eat.meal.data.BasicMeal;

import java.util.List;

public interface IMenuService {

    List<BasicMeal> getAllAvailableMeals();

    BasicMeal getMealForDate(String dateString);
}

```

## `src/main/java/de/schneider21/what2eat/meal/business/IWeatherService.java`

```java
package de.schneider21.what2eat.meal.business;

public interface IWeatherService {

    Double getTemperatureInCelsius(String cityName, String countryCode, String dateString);
}

```

## `src/main/java/de/schneider21/what2eat/meal/business/MealService.java`

```java
package de.schneider21.what2eat.meal.business;

import de.schneider21.what2eat.meal.data.BasicMeal;
import de.schneider21.what2eat.meal.data.ExtendedMeal;

import java.util.List;
import java.util.Objects;

public class MealService implements IMealService {

    private IMenuService menuService;
    private IWeatherService weatherService;

    public MealService(IMenuService menuService, IWeatherService weatherService) {
        Objects.requireNonNull(menuService);
        this.menuService = menuService;
        Objects.requireNonNull(weatherService);
        this.weatherService = weatherService;
    }

    @Override
    public List<BasicMeal> getAllAvailableMeals() {
        return menuService.getAllAvailableMeals();
    }

    @Override
    public ExtendedMeal getExtendedMealForDate(String dateString) {
        final BasicMeal meal = menuService.getMealForDate(dateString);
        if (meal == null) {
            return null;
        }
        final Double temperatureInCelsius = weatherService.getTemperatureInCelsius("Kaiserslautern", "DE", dateString);
        if (temperatureInCelsius != null) {
            System.out.printf("MealService: Temperature received is %.2f°C\n", temperatureInCelsius);
        } else {
            System.out.printf("MealService: No temperature value could be found\n");
        }
        int coldBowlProbabilityInPercent = calculateColdBowlProbabilityInPercent(temperatureInCelsius);
        ExtendedMeal extendedMeal = new ExtendedMeal(meal.getDate(), meal.getTitle(), meal.getPrice(),
                coldBowlProbabilityInPercent);
        return extendedMeal;
    }

    @Override
    public int calculateColdBowlProbabilityInPercent(Double temperature) {
        if (temperature == null) {
            return -1;
        }
        return Math.toIntExact(Math.round(Math.max(0, Math.min(100, (temperature - 20) * 10))));
    }
}

```

## `src/main/java/de/schneider21/what2eat/meal/business/MensaKlService.java`

```java
package de.schneider21.what2eat.meal.business;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;
import de.schneider21.what2eat.meal.data.BasicMeal;
import okhttp3.HttpUrl;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class MensaKlService implements IMenuService {

    private static final String API_URL = "http://www.mensa-kl.de/api.php";
    private static final Set<String> VALID_LOCATIONS = Set.of("1", "2", "1veg", "2veg");

    /**
     * This is the format as returned by the mensa-kl API
     */
    @JsonIgnoreProperties(ignoreUnknown = true)
    static class LunchEntry {
        //{
        //	"m_id": "43345",
        //	"date": "2019-01-21",
        //	"loc": "1",
        //	"title": "Rahmbraten  mit Brasilsoße, Pommes frites und Salat",
        //	"price": "4.05",
        //	"rating": "3.9",
        //	"rating_amt": "10",
        //	"image": "md4h4ju8a9lz6wx.jpg",
        //	"icon": "pork"
        //}

        private String date, loc, title, price, rating;

        public String getDate() {
            return date;
        }

        public void setDate(String date) {
            this.date = date;
        }

        public String getLoc() {
            return loc;
        }

        public void setLoc(String loc) {
            this.loc = loc;
        }

        public String getTitle() {
            return title;
        }

        public void setTitle(String title) {
            this.title = title;
        }

        public String getPrice() {
            return price;
        }

        public void setPrice(String price) {
            this.price = price;
        }

        public String getRating() {
            return rating;
        }

        public void setRating(String rating) {
            this.rating = rating;
        }
    }

    private final OkHttpClient client = new OkHttpClient();
    private final ObjectMapper mapper = new ObjectMapper();

    public List<BasicMeal> getAllAvailableMeals() {

        HttpUrl.Builder urlBuilder = HttpUrl
                .parse(API_URL)
                .newBuilder()
                .addQueryParameter("date", "all")
                .addQueryParameter("format", "json");
        String url = urlBuilder.build().toString();

        Request request = new Request.Builder()
                .url(url)
                .build();

        try {
            final Response response = client.newCall(request).execute();
            return parseAndFilterListResponse(bodyOrEmptyArrayIfError(response))
                    .stream()
                    .map(lunchEntry -> convertToMeal(lunchEntry))
                    .collect(Collectors.toList());
        } catch (IOException e) {
            System.out.println("MealService: Exception when listing all lunch entries");
            e.printStackTrace();
            return Collections.emptyList();
        }
    }

    public BasicMeal getMealForDate(String date) {

        HttpUrl.Builder urlBuilder = HttpUrl
                .parse(API_URL)
                .newBuilder()
                .addQueryParameter("date", date)
                .addQueryParameter("format", "json");
        String url = urlBuilder.build().toString();

        Request request = new Request.Builder()
                .url(url)
                .build();

        try {
            final Response response = client.newCall(request).execute();
            final List<LunchEntry> meals = parseAndFilterListResponse(bodyOrEmptyArrayIfError(response));
            if (meals.isEmpty()) {
                return null;
            }
            return convertToMeal(meals.get(0));
        } catch (IOException e) {
            System.out.println("MealService: Exception when listing meals for " + date);
            e.printStackTrace();
            return null;
        }
    }

    private String bodyOrEmptyArrayIfError(Response response) throws IOException {
        final String body = response.body().string();
        System.out.println("MensaKlService: Body (all locations): " + body);
        if (!body.startsWith("-1")) {
            return body;
        }
        System.out.println("MensaKlService: no results found");
        return "[]";
    }

    List<LunchEntry> parseAndFilterListResponse(String body) throws IOException {
        List<LunchEntry> lunchEntries = new ObjectMapper().reader()
                .forType(mapper.getTypeFactory().constructCollectionType(List.class, LunchEntry.class))
                .readValue(body.replace("\t", " "));
        return lunchEntries.stream()
                .filter(entry -> VALID_LOCATIONS.contains(entry.getLoc()))
                .collect(Collectors.toList());
    }

    private BasicMeal convertToMeal(LunchEntry lunchEntry) {
        BasicMeal meal = new BasicMeal(lunchEntry.getDate(), lunchEntry.getTitle(),
                new BigDecimal(lunchEntry.getPrice()));
        return meal;
    }
}

```

## `src/main/java/de/schneider21/what2eat/meal/business/WeatherBitService.java`

```java
package de.schneider21.what2eat.meal.business;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.HttpUrl;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Properties;

public class WeatherBitService implements IWeatherService {

    private static final String CONFIG_FILE = "./src/main/resources/weatherbit.properties";

    private final OkHttpClient client = new OkHttpClient();
    private final ObjectMapper mapper = new ObjectMapper();
    private final String apiKey;

    public WeatherBitService() {
        Properties weatherBitConfig = loadConfig();
        String apiKey = weatherBitConfig.getProperty("apiKey");
        if (apiKey == null || apiKey.isEmpty()) {
            throw new IllegalStateException("No apiKey defined in " + CONFIG_FILE);
        }
        this.apiKey = apiKey;
    }

    private Properties loadConfig() {
        try (InputStream input = new FileInputStream(CONFIG_FILE)) {
            Properties config = new Properties();
            config.load(input);
            return config;
        } catch (IOException ex) {
            throw new IllegalStateException("Error loading " + CONFIG_FILE, ex);
        }
    }

    private ForecastResponse parseWeatherResponse(String body) throws IOException {
        return mapper.readerFor(ForecastResponse.class)
                .readValue(body);
    }

    @Override
    public Double getTemperatureInCelsius(String cityName, String countryCode, String dateString) {
        HttpUrl.Builder urlBuilder = HttpUrl
                .parse("https://api.weatherbit.io/v2.0/forecast/daily")
                .newBuilder();
        urlBuilder.addQueryParameter("city", cityName)
                .addQueryParameter("country", countryCode)
                .addQueryParameter("key", apiKey);
        String url = urlBuilder.build().toString();

        Request request = new Request.Builder()
                .url(url)
                .build();

        System.out.printf("WeatherBitService: Requesting weather data for %s (%s)\n", cityName, countryCode);
        try {
            final Response response = client.newCall(request).execute();
            if (!response.isSuccessful()) {
                System.out.printf("Could not get weather, got status %s and body %s\n", response.code(),
                        response.body().string());
                return null;
            }
            final ForecastResponse forecastResponse = parseWeatherResponse(response.body().string());
            // example response: ForecastResponse{data=[ForecastData{datetime='2020-02-25', max_temp='8.4'},
            // ForecastData{datetime='2020-02-26', max_temp='4.3'}, ForecastData{datetime='2020-02-27', max_temp='2.7'},
            // ForecastData{datetime='2020-02-28', max_temp='5.1'}, ForecastData{datetime='2020-02-29', max_temp='8
            // .3'}, ...
            // (16 days from current date)
            return forecastResponse.getData().stream()
                    .filter(data -> dateString.equals(data.getDatetime()))
                    .map(ForecastData::getMax_temp)
                    .findFirst()
                    .orElse(null);
        } catch (IOException e) {
            System.out.println("Could not get weather: " + e.getMessage());
            return null;
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    private static class ForecastData {
        double max_temp;
        String datetime;

        public ForecastData() {
        }

        public double getMax_temp() {
            return max_temp;
        }

        public void setMax_temp(double max_temp) {
            this.max_temp = max_temp;
        }

        public String getDatetime() {
            return datetime;
        }

        public void setDatetime(String datetime) {
            this.datetime = datetime;
        }

        @Override
        public String toString() {
            return "ForecastData{" +
                    "datetime='" + datetime + '\'' +
                    ", max_temp='" + max_temp + '\'' +
                    '}';
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    private static class ForecastResponse {

        private List<ForecastData> data;

        public List<ForecastData> getData() {
            return data;
        }

        public void setData(List<ForecastData> data) {
            this.data = data;
        }

        @Override
        public String toString() {
            return "ForecastResponse{" +
                    "data=" + data +
                    '}';
        }
    }

}

```

## `src/main/java/de/schneider21/what2eat/meal/data/BasicMeal.java`

```java
package de.schneider21.what2eat.meal.data;

import java.math.BigDecimal;

public class BasicMeal {

    // For a real system, it would be more robust to use Date or long instead of string here
    private String date;
    private String title;
    private BigDecimal price;

    public BasicMeal(String date, String title, BigDecimal price) {
        this.date = date;
        this.title = title;
        this.price = price;
    }

    public String getDate() {
        return date;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public void setPrice(BigDecimal price) {
        this.price = price;
    }

    @Override
    public String toString() {
        return "BasicMeal{" +
                "date='" + date + '\'' +
                ", title='" + title + '\'' +
                ", price=" + price +
                '}';
    }
}

```

## `src/main/java/de/schneider21/what2eat/meal/data/ExtendedMeal.java`

```java
package de.schneider21.what2eat.meal.data;

import java.math.BigDecimal;

public class ExtendedMeal extends BasicMeal {

    private int coldBowlProbabilityInPercent;

    public ExtendedMeal(String date, String title, BigDecimal price, int coldBowlProbabilityInPercent) {
        super(date, title, price);
        this.coldBowlProbabilityInPercent = coldBowlProbabilityInPercent;
    }

    /**
     * returns the probability that a cold bowl is served with the meal. A return value of -1 means that the probability
     * could not be calculated.
     *
     * @return
     */
    public int getColdBowlProbabilityInPercent() {
        return coldBowlProbabilityInPercent;
    }

    public void setColdBowlProbabilityInPercent(int coldBowlProbabilityInPercent) {
        this.coldBowlProbabilityInPercent = coldBowlProbabilityInPercent;
    }

    @Override
    public String toString() {
        return "ExtendedMeal{" +
                "date='" + getDate() + '\'' +
                ", title='" + getTitle() + '\'' +
                ", price=" + getTitle() +
                ", coldBowlProbabilityInPercent=" + coldBowlProbabilityInPercent +
                '}';
    }
}

```

## `src/test/java/UmlPrinter.java`

```java
import de.schneider21.what2eat.ServiceFactory;
import de.schneider21.what2eat.framework.HttpServer;
import de.schneider21.what2eat.framework.RestController;
import de.schneider21.what2eat.meal.api.MealController;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.reflect.Parameter;
import java.util.Arrays;
import java.util.Comparator;
import java.util.StringJoiner;

public class UmlPrinter {

    public static void main(String[] args) {
//        Class<?>[] classes = {MealService.class, WeatherBitService.class, MensaKlService.class,
//                BasicMeal.class, ExtendedMeal.class};
        Class<?>[] classes = {RestController.IRequestParameters.class, RestController.class, HttpServer.class,
                MealController.class,
                ServiceFactory.class};
        for (Class<?> clazz : classes) {
            printUml(clazz);
        }
    }

    private static void printUml(Class<?> clazz) {
        if (Modifier.isInterface(clazz.getModifiers())) {
            System.out.println("<<Interface>>");
        }
        System.out.println(clazz.getSimpleName());
        System.out.println("----------------------------");
        Arrays.stream(clazz.getDeclaredConstructors())
                .sorted(Comparator.comparing(Constructor::getName))
                .forEach(constructor -> {
                    printModifier(constructor.getModifiers());
                    System.out.print(clazz.getSimpleName());
                    printParameters(constructor.getParameters());
                    System.out.println();
                });

        System.out.println("----------------------------");
        Arrays.stream(clazz.getDeclaredMethods())
                .sorted(Comparator.comparing(Method::getName))
                .forEach(method -> {
                    printModifier(method.getModifiers());
                    System.out.print(method.getName());
                    printParameters(method.getParameters());
                    System.out.println(" : " + method.getReturnType().getSimpleName());
                });

        System.out.println();
        System.out.println();
    }

    private static void printParameters(Parameter[] parameters) {
        StringJoiner joiner = new StringJoiner(", ", "(", ")");
        for (Parameter type : parameters) {
            String s = type.getName() + ": " + type.getType().getSimpleName();
            joiner.add(s);
        }
        System.out.print(joiner);
    }

    private static void printModifier(int modifiers) {
        if (Modifier.isPublic(modifiers)) {
            System.out.print("+ ");
            return;
        }
        if (Modifier.isPrivate(modifiers)) {
            System.out.print("- ");
            return;
        }
        if (Modifier.isProtected(modifiers)) {
            System.out.print("# ");
            return;
        }
        System.out.print("~ ");
    }
}


```

## `src/test/java/de/schneider21/what2eat/meal/business/ExampleData.java`

```java
package de.schneider21.what2eat.meal.business;

import de.schneider21.what2eat.meal.data.BasicMeal;

import java.math.BigDecimal;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class ExampleData {

    public static final List<BasicMeal> EXAMPLE_MEALS;

    static {
        List<BasicMeal> meals = new ArrayList<>();
        meals.add(new BasicMeal(new SimpleDateFormat("YYYY-MM-dd").format(new Date()),
                "Tagesspezial: Schnitzel mit Pommes und Salat (SchniPoSa)",
                new BigDecimal("2.65")));
        meals.add(new BasicMeal("2020-03-23",
                "Gebratene Hähnchenkeule  mit Mexikana-Salsa, Steakhouse-Fries und Weißkrautsalat \\\"Coleslaw\\\"",
                new BigDecimal("2.65")));
        meals.add(new BasicMeal("2020-03-24", "Maultaschen mit Fleischfüllung, Kartoffel-Käse-Soße  und Salat",
                new BigDecimal("2.65")));
        meals.add(new BasicMeal("2020-03-25", "Paniertes Schweineschnitzel  mit Rahmsoße, Spätzle  und Salat",
                new BigDecimal("2.65")));
        meals.add(new BasicMeal("2020-03-26", "Rindersaftgulasch  mit hausgemachtem Karotten-Kartoffelstampf und Salat",
                new BigDecimal("2.65")));
        meals.add(new BasicMeal("2020-03-27", "Indisches Fischcurry mit Seelachs und Gemüse, Duftreis und Salat",
                new BigDecimal("2.65")));

        meals.add(new BasicMeal("2020-03-30", "Falafel mit \"Ras el Hanout\"-Soße, orientalischem Reis und Salat",
                new BigDecimal("2.65")));
        meals.add(
                new BasicMeal("2020-03-31", "Geschmorte Lammkeule \"Provencial\" mit Burgundersoße und Pariser " +
                        "Kartoffeln",
                        new BigDecimal("2.65")));
        meals.add(new BasicMeal("2020-04-01",
                "\"Fajita Pueblo\" mit Paprika, Zucchini und Zwiebeln, dazu Sour-Cream-Dip, Tortillas und Salat",
                new BigDecimal("2.65")));
        meals.add(new BasicMeal("2020-04-02", "Hähnchenbrustfilet, Ratatouillegemüse, Thymiankartoffeln und Salat",
                new BigDecimal("2.65")));
        meals.add(new BasicMeal("2020-04-03", "'Dibbelabbes': Saarländischer Kartoffelauflauf mit Lauch, dazu Apfelmus",
                new BigDecimal("2.65")));

        EXAMPLE_MEALS = meals;
    }
}

```

## `src/test/java/de/schneider21/what2eat/meal/business/IncreaseCoverageDummyTest.java`

```java
package de.schneider21.what2eat.meal.business;

import org.junit.jupiter.api.Test;

/**
 * This is an example how one can increase test coverage drastically without any actual benefit since the test is
 * useless (no assert used, and the weather service even logs an error!)
 */
public class IncreaseCoverageDummyTest {

    @Test
    public void test() {
        new MensaKlService().getAllAvailableMeals();
        new WeatherBitService().getTemperatureInCelsius(null, null, null);
    }
}

```

## `src/test/java/de/schneider21/what2eat/meal/business/MealServiceSimpleMockTest.java`

```java
package de.schneider21.what2eat.meal.business;

import de.schneider21.what2eat.meal.data.BasicMeal;
import de.schneider21.what2eat.meal.data.ExtendedMeal;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * This test shows how to do a module test of MealService using simple mock implementations for
 * IMenuService and IWeatherService.
 */
class MealServiceSimpleMockTest {

    static final BasicMeal BASIC_MEAL = new BasicMeal("2021-11-11", "Schneckengulasch", new BigDecimal("3.33"));

    static class MockMensaKlService implements IMenuService {

        @Override
        public List<BasicMeal> getAllAvailableMeals() {
            throw new UnsupportedOperationException("Not implemented in this mock");
        }

        @Override
        public BasicMeal getMealForDate(String date) {
            return BASIC_MEAL;
        }
    }

    static class MockWeatherService implements IWeatherService {

        private double temperature;

        public MockWeatherService(double temperature) {
            this.temperature = temperature;
        }

        @Override
        public Double getTemperatureInCelsius(String cityName, String countryCode, String dateString) {
            return temperature;
        }
    }

    @Test
    void testGetExtendedMealForDate() {
        // No "hacks" are needed here - we can just inject our mock services via the constructor
        MealService mealService = new MealService(new MockMensaKlService(), new MockWeatherService(21.5));

        // When we now call the mealService method, our mock services will be used
        ExtendedMeal extendedMeal = mealService.getExtendedMealForDate(BASIC_MEAL.getDate());

        assertEquals(BASIC_MEAL.getDate(), extendedMeal.getDate());
        assertEquals(BASIC_MEAL.getTitle(), extendedMeal.getTitle());
        assertEquals(BASIC_MEAL.getPrice(), extendedMeal.getPrice());
        // 21.5°C means 15% cold bowl probability
        assertEquals(15, extendedMeal.getColdBowlProbabilityInPercent());
    }
}
```

## `src/test/java/de/schneider21/what2eat/meal/business/MealServiceTest.java`

```java
package de.schneider21.what2eat.meal.business;

import de.schneider21.what2eat.meal.data.BasicMeal;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

class MealServiceTest {

    private IMealService mealService;
    private IWeatherService weatherService;

    private final BasicMeal meal1 = new BasicMeal("2020-03-01", "Kaviar mit Pommes", new BigDecimal("20.00"));
    private final BasicMeal meal2 =
            new BasicMeal("2020-03-02", "Schneckenauflauf mit Fischstäbchen", new BigDecimal("1.10"));
    private final BasicMeal meal3 =
            new BasicMeal("2020-03-03", "Saure Gurken mit roter Grütze", new BigDecimal("2.70"));

    @BeforeEach
    void setUp() {
        weatherService = new IWeatherService() {
            @Override
            public Double getTemperatureInCelsius(String cityName, String countryCode, String dateString) {
                return null;
            }
        };
        mealService = new MealService(
                new MockMenuService(
                        Arrays.asList(meal1, meal2, meal3)
                ), weatherService
        );
    }

    @AfterEach
    void tearDown() {
    }

    private static void assertEqual(BasicMeal expected, BasicMeal actual) {
        if (expected == null) {
            assertNull(actual);
            return;
        }
        // from here: expected is not null
        assertNotNull(actual);
        assertEquals(expected.getDate(), actual.getDate());
        assertEquals(expected.getTitle(), actual.getTitle());
        assertEquals(expected.getPrice(), actual.getPrice());
    }

    @Test
    void getMealForDate_mealPresent() {
        final BasicMeal expected = meal2;
        final BasicMeal actual = mealService.getExtendedMealForDate("2020-03-02");
        assertEqual(expected, actual);
    }

    @Test
    void getMealForDate_mealNotPresent() {
        final BasicMeal notExisting = mealService.getExtendedMealForDate("2019-03-02");
        assertNull(notExisting);
    }

    @Test
    void calculateColdBowlProbabilityInPercent() {
        assertEquals(-1, mealService.calculateColdBowlProbabilityInPercent(null));
        assertEquals(0, mealService.calculateColdBowlProbabilityInPercent(-1.0));
        assertEquals(0, mealService.calculateColdBowlProbabilityInPercent(0.0));
        assertEquals(0, mealService.calculateColdBowlProbabilityInPercent(19.0));
        assertEquals(0, mealService.calculateColdBowlProbabilityInPercent(19.9));
        assertEquals(0, mealService.calculateColdBowlProbabilityInPercent(20.0));

        assertEquals(10, mealService.calculateColdBowlProbabilityInPercent(21.0));
        assertEquals(47, mealService.calculateColdBowlProbabilityInPercent(24.7));
        assertEquals(50, mealService.calculateColdBowlProbabilityInPercent(25.0));
        assertEquals(99, mealService.calculateColdBowlProbabilityInPercent(29.9));

        assertEquals(100, mealService.calculateColdBowlProbabilityInPercent(30.0));
        assertEquals(100, mealService.calculateColdBowlProbabilityInPercent(30.1));
        assertEquals(100, mealService.calculateColdBowlProbabilityInPercent(40.14));
        assertEquals(100, mealService.calculateColdBowlProbabilityInPercent(100.0));
    }
}
```

## `src/test/java/de/schneider21/what2eat/meal/business/MensaKlServiceTest.java`

```java
package de.schneider21.what2eat.meal.business;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class MensaKlServiceTest {

    private MensaKlService mensaKlService;

    @BeforeEach
    public void setup() {
        mensaKlService = new MensaKlService();
    }

    @Test
    public void parseAndFilterListResponse_emptyArray() throws IOException {
        String input = "[]";

        List<MensaKlService.LunchEntry> lunchEntries = mensaKlService.parseAndFilterListResponse(input);

        assertEquals(0, lunchEntries.size());
    }

    @Test
    public void parseAndFilterListResponse_singletonArrayWantedEntry() throws IOException {
        String input = """
                        [
                            {
                                "m_id": 48541,
                                "date": "2022-11-29",
                                "loc": "1veg",
                                "title": "Pommes frites und Salat",
                                "title_with_additives": "Pommes frites und Salat",
                                "price": "3.50",
                                "rating": 3.4,
                                "rating_amt": 18,
                                "image": "cedfqvairkgwk0p.jpg",
                                "icon": "pork"
                            }
                        ]
                """;

        List<MensaKlService.LunchEntry> lunchEntries = mensaKlService.parseAndFilterListResponse(input);

        assertEquals(1, lunchEntries.size());
        assertEquals("1veg", lunchEntries.get(0).getLoc());
    }

    @Test
    public void parseAndFilterListResponse_singletonArrayUnwantedEntry() throws IOException {
        String input = """
                        [
                            {
                                "m_id": 48581,
                                "date": "2022-11-29",
                                "loc": "Bistro36",
                                "title": "Sp\\u00e4tzle-Sauerkraut-Pfanne mit R\\u00f6stzwiebeln",
                                "title_with_additives": "Sp\\u00e4tzle-Sauerkraut-Pfanne mit R\\u00f6stzwiebeln (1,Gl,So)",
                                "price": "2.75",
                                "rating": 0,
                                "rating_amt": 0,
                                "image": "",
                                "icon": ""
                            }
                        ]
                """;

        List<MensaKlService.LunchEntry> lunchEntries = mensaKlService.parseAndFilterListResponse(input);

        assertEquals(0, lunchEntries.size());
    }

    @Test
    public void parseAndFilterListResponse_withUnwantedLocations() throws IOException {
        String input = """
                        [
                            {
                                "m_id": 48571,
                                "date": "2022-11-29",
                                "loc": "News",
                                "title": "Bei Instagram @studierendenwerk_kl und auf der Studierendenwerk-Website werden schon Bilder des diesj\\u00e4hrigen Weihnachtsmen\\u00fcs [\\ud83c\\udf84 7. Dezember an der TUK] gezeigt.",
                                "title_with_additives": "Bei Instagram @studierendenwerk_kl und auf der Studierendenwerk-Website werden schon Bilder des diesj\\u00e4hrigen Weihnachtsmen\\u00fcs [\\ud83c\\udf84 7. Dezember an der TUK] gezeigt.",
                                "price": "",
                                "rating": 0,
                                "rating_amt": 0,
                                "image": "",
                                "icon": ""
                            },
                            {
                                "m_id": 48541,
                                "date": "2022-11-29",
                                "loc": "1",
                                "title": "Rahmbraten  mit Brasilso\\u00dfe, Pommes frites und Salat",
                                "title_with_additives": "Rahmbraten (S) mit Brasilso\\u00dfe (Gl,La), Pommes frites und Salat",
                                "price": "3.50",
                                "rating": 3.4,
                                "rating_amt": 18,
                                "image": "cedfqvairkgwk0p.jpg",
                                "icon": "pork"
                            },
                            {
                                "m_id": 48542,
                                "date": "2022-11-29",
                                "loc": "2veg",
                                "title": "Vollkornnudeln  mit veganer Champignon-Rahmso\\u00dfe  und Rotkrautsalat",
                                "title_with_additives": "Vollkornnudeln (1,Gl) mit veganer Champignon-Rahmso\\u00dfe (1,Gl,So) und Rotkrautsalat",
                                "price": "2.75",
                                "rating": 3.5,
                                "rating_amt": 4,
                                "image": "nin5erl22f9n59c.jpg",
                                "icon": ""
                            },
                            {
                                "m_id": 48586,
                                "date": "2022-11-29",
                                "loc": "Feelgood",
                                "title": "Reis mit Chili sin Carne und Limetten-Dip",
                                "title_with_additives": "Reis mit Chili sin Carne und Limetten-Dip (La)",
                                "price": "3.95",
                                "rating": 0,
                                "rating_amt": 0,
                                "image": "",
                                "icon": ""
                            },
                            {
                                "m_id": 48581,
                                "date": "2022-11-29",
                                "loc": "Bistro36",
                                "title": "Sp\\u00e4tzle-Sauerkraut-Pfanne mit R\\u00f6stzwiebeln",
                                "title_with_additives": "Sp\\u00e4tzle-Sauerkraut-Pfanne mit R\\u00f6stzwiebeln (1,Gl,So)",
                                "price": "2.75",
                                "rating": 0,
                                "rating_amt": 0,
                                "image": "",
                                "icon": ""
                            }
                        ]
                """;

        List<MensaKlService.LunchEntry> lunchEntries = mensaKlService.parseAndFilterListResponse(input);

        assertEquals(2, lunchEntries.size());
        assertEquals("1", lunchEntries.get(0).getLoc());
        assertEquals("2veg", lunchEntries.get(1).getLoc());
    }
}
```

## `src/test/java/de/schneider21/what2eat/meal/business/MockMenuService.java`

```java
package de.schneider21.what2eat.meal.business;

import de.schneider21.what2eat.meal.data.BasicMeal;

import java.util.Collections;
import java.util.List;

public class MockMenuService implements IMenuService {

    private List<BasicMeal> allMeals;

    public MockMenuService(List<BasicMeal> allMeals) {
        this.allMeals = allMeals;
    }

    public List<BasicMeal> findAllSortByDateAsc() {
        return Collections.unmodifiableList(allMeals);
    }

    @Override
    public List<BasicMeal> getAllAvailableMeals() {
        return allMeals;
    }

    @Override
    public BasicMeal getMealForDate(String dateString) {
        return allMeals
                .stream()
                .filter(m -> m.getDate().equals(dateString))
                .findAny()
                .orElse(null);
    }
}

```


# What2Eat - Architecture documentation

## 1. Introduction

What2Eat is a simple app for showing the meal of the day at the cafeteria of the university of Kaiserslautern. It serves as an example for illustrating architecture design (part of the lecture "SWAR-WIN: Softwarearchitektur" by Prof. Dr. Johannes C. Schneider from [HTWG Konstanz](https://www.htwg-konstanz.de/)).

### 1.1. Business context

The following "business" goals have been identified for this project:

**G1.** System should serve as an educational example to show design process and application of architectural styles and patterns.

**G2.** Students with WebTech-Knowledge should be able to implement the Web UI part.

### 1.2. System overview

The purpose of the system is on the one hand to offer certain functionality (cafeteria menu with cold bowl probability, as explained in later sections), but on the other hand (and much more important!), to serve as an easily comprehensible example for the target group (WIN students).

Furthermore, while a real world application would consist of a frontend and server part, this documentation focuses on the server part which uses Java - a technology WIN students are familiar with.

### 1.3. Stakeholders

Stakeholders of this project and system are

- the teacher of the lecture _Software-Architektur_ (project lead),
- attendants of the lecture _Software-Architektur_, WIN and GIB students ("users" in terms of learning about software architecture) and
- potential cafeteria customers (end users).

### 1.4. Constraints

The following constraints have been identified:

**C1.** The cafeteria web page is slow and not optimized for smart phone usage.

**C2.** WIN students should be familiar with system's main technology stack, in particular they should have practical experience with the programming language.

**C3.** Based on a analysis using a sample size of 10 meals during different weather conditions, a (self-called) data scientist came up with the following formula to calculate the probability of cold bowl serving:

- Let x be the forecast temperature for the day at 12 o'clock and p be the probability that a cold bowl is served:
  - If x < 20°C, then p = 0%.
  - If 20°C ≤ x ≤ 30°C, then p = (x – 20)⋅10%
    Example: x = 23.7°C means p = 37%
  - If x ≥ 30°C, then p = 100%.

**C4.** All external services used by the system must be free to use.

### 1.5. Document goals

The intent of this documents on one side is to give an example for a software documentation. On the other side, it should illustrate the architecture of the system. The main target group for this documentation are the attendants of the lecture _Software-Architektur_.

This document represents the system's state as implemented in branch `with-cache` in the [What2Eat GitHub repository](https://github.com/neshanjo/what2eat). The implementation covers only the backend part of the system. Also this document is mainly describing the backend part of the system.

## 2. System context and domain

The system relies on data that is queried by external system. The following sections give more information about the scope of the architecture and the main data used within the system.

### 2.1. System context delineation

The system scope and context has been identified as follows:

![system-context](diagrams/system-context-RT.drawio.png)

There is a single user type interacting with the system. Decisions have been made to use weather and menu data from external systems. Entering menu data manually was discarded since it requires continuos work at least twice a month by an operating person as the meals are only available two week in advance. Another idea of using a self-built weather station to measure and predict the temperature was discarded since there are free weather services with a more precise forecast.

### 2.2. Domain model

In this relatively small system, there are two domains: Meals and weather. Weather data is mainly handled in an external system.

In the following figure, the main entities used in the system are depicted.

![domain model](diagrams/domain-model-RT.drawio.png)

The data model is refined further in the section [4.3. Data model](#43-data-model).

## 3. Architecture drivers (function and quality)

Software architecture is driven by business goals, constraints, functional requirements and quality attributes of the system. The first two types can be found in [1.1. Business Context](#11-business-context) and [1.4. Constraints](#14-constraints), while the latter two types of drivers are described in this chapter.

### 3.1. Key functional requirements

The key functional requirements are given in the form of user stories.

F1. As a hungry student, I would like to know what meals are offered today in the cafeteria without having to go there in order to decide if I go to the cafeteria or bring my own food.

F2. As a hungry student, I would like to know what today‘s meals in the cafeteria cost without having to go there in order to decide if I go to the cafeteria or prefer something cheaper from the local bakery of kebap place.

F3. As a hungry student, I would like to know if there will be a cold bowl (see [8. Glossary](#8-glossary)) offered in the cafeteria because then I don't have to buy a drink. (Note: This information is not shown on the cafeteria menu and cannot be seen unless actually queuing for the meal)

### 3.2. Quality attributes

Quality attributes are described in form of the architecture scenario template. Status and Priority are omitted.

**Description** | | **Quantification** |
| Environment | A developer has a computer with working internet connection and standard WIN dev environment: Java version J is installed, IntelliJ version I, git version G and Maven version M installed. | Internet bandwidth &ge; 1 MBit/s, J &ge; 17, I &ge; 2021.3, G &ge; 2.33, M &ge; 3.8 |
| Stimulus | The developer wants to checkout and run the project for local testing. | |
| Response | The system is running and answering the first request in T. | T &le; 5 minutes |

| Categorization  |                                                                                |                    |
| --------------- | ------------------------------------------------------------------------------ | ------------------ |
| Scenario Name   | Code comprehensibility                                                         |                    |
| Scenario ID     | Q.Comprehensibility                                                            |                    |
| **Description** |                                                                                | **Quantification** |
| Environment     | A WIN student in semester S has checked out the project and started the system | S &ge; 6           |
| Stimulus        | The student executes a function of the system.                                 |                    |
| Response        | The student can find the code responsible for implementing the function in T.  | T &le; 5 minutes   |

| Categorization  |                                                                                                                |                    |
| --------------- | -------------------------------------------------------------------------------------------------------------- | ------------------ |
| Scenario Name   | Package Size                                                                                                   |                    |
| Scenario ID     | Q.Size                                                                                                         |                    |
| **Description** |                                                                                                                | **Quantification** |
| Environment     | The code is ready for a new deployment.                                                                        |                    |
| Stimulus        | A new deployment artifact is built to update the production app.                                               |                    |
| Response        | In order to make the deployment from places with weak internet connection, the deployment artifact has size S. | S &le; 3 MB        |

| Categorization  |                                                                     |                                                                                                                                                                                                                                                                                                                   |
| --------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Scenario Name   | Simple one-user educational system                                  |                                                                                                                                                                                                                                                                                                                   |
| Scenario ID     | Q.Performance.Threads                                               |                                                                                                                                                                                                                                                                                                                   |
| **Description** |                                                                     | **Quantification**                                                                                                                                                                                                                                                                                                |
| Environment     | The system is running.                                              |                                                                                                                                                                                                                                                                                                                   |
| Stimulus        | The system gets x parallel requests                                 | x = 1 (_simple educational system, no parallelism required!_)                                                                                                                                                                                                                                                     |
| Response        | The system is able to handle the requests without noticeable delay. | If x > 1, the second, third, ... requests gets a response with at most 10ms delay compared to the first request (_Since x == 1, the case x > 1 will not occur in this simple system. This is just an example how a parallelism driver could be formulated, given that the system should handle parallel request_) |

| Categorization  |                                                                                  |                                                  |
| --------------- | -------------------------------------------------------------------------------- | ------------------------------------------------ |
| Scenario Name   | (Almost) instant meal display                                                    |                                                  |
| Scenario ID     | Q.Performance.Response                                                           |                                                  |
| **Description** |                                                                                  | **Quantification**                               |
| Environment     | The system is running. The cafeteria is open on the current day.                 |                                                  |
| Stimulus        | A user requests the meal(s) of today.                                            |                                                  |
| Response        | The system shows the meal(s) of today along with the cold bowl probability in T. | T &le; 200 ms for 99 of 100 consecutive requests |

| Categorization  |                                                                                                                                                                                     |                                    |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Scenario Name   | Offline testability                                                                                                                                                                 |                                    |
| Scenario ID     | Q.Testability.Offline                                                                                                                                                               |                                    |
| **Description** |                                                                                                                                                                                     | **Quantification**                 |
| Environment     | A developer has set up the project for local development and testing. There is internet connection on the computer. The developer executes all unit and module tests. x tests pass. | x = number of passed tests         |
| Stimulus        | The developer goes offline and executes unit and module tests again.                                                                                                                | Internet bandwidth = 0 Mbit/s      |
| Response        | The same x tests pass.                                                                                                                                                              | Number of passed tests is still x. |

| Categorization  |                                                                                                       |                                                                    |
| --------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Scenario Name   | Weather testability                                                                                   |                                                                    |
| Scenario ID     | Q.Testability.Weather                                                                                 |                                                                    |
| **Description** |                                                                                                       | **Quantification**                                                 |
| Environment     | A developer has set up the project for local development and testing. It is winter in Kaiserslautern. | temperature in Kaiserslautern < 20°C                               |
| Stimulus        | The developer wants to test for different cold bowl probability values.                               | cold bowl probability values 0%, 1%, 21%, 45%, 50%, 78%, 99%, 100% |
| Response        | The developer is able to write and execute tests that return the desired probability values.          |                                                                    |

## 4. System decomposition

During architecture design, the system has been decomposed with respect to different criteria, i.e. functional-driven, data-driven, deployment-driven and technology driven. The resulting architecture is described in the following sections.

### 4.1. Solution approach and key architecture decisions

The key design decision is to use different components for data display and data acquisition.

![coarse functional decomposition](diagrams/coarse-functional-decomposition-RT.drawio.png)

This concept is further refined by applying the client-server pattern, see [4.6. Deployment and Operation](#46-deployment-and-operation).

### 4.2. System structure

The system is decomposed into several components that all have their own concerns.

![system structure](diagrams/system-structure-RT.drawio.png)

Design decisions:

- MealService as central service, WeatherService and MenuService as subservices that will query the external system.

### 4.3. Data model

The figure from the last section already illustrated the intended data flow between the components. This is the data model in more detail:

![system data](diagrams/system-data-RT.drawio.png)

Design decisions:

- We have modelled separate data entities for query and response.

### 4.4. Code organization (mapping runtime to devtime)

Components are mapped 1:1 to modules for realizing the components at devtime, see the following two figures.

![functional decomposition at runtime](diagrams/functional-driven-decomposition-services-RT.drawio.png)

![functional decomposition at devtime](diagrams/functional-driven-decomposition-backend-DT.drawio.png)

Note that the realization of the modules is done with the help of additional libraries.

Design decisions:

- The runtime decomposition already follows the principle of separation of concerns. This is continued at devtime by using the 1:1 mapping.

Discarded Alternatives:

- The modules are not split up any further since their functionality is already quite simple and limited.

### 4.5. Build Process

To build a releasable and deployable JAR file, the Maven package command can be used. However, currently, the system is built and run within IntelliJ IDE only and used for local testing and demonstration.

### 4.6. Deployment and Operation

The system is decomposed into a client and a server part. These correspond to the Meal display and meal data acquisition components. During development, both client and server can be run on the same machine:

![deployment-driven-decomposition-DT](diagrams/deployment-driven-decomposition-DT.drawio.png)

This will be the typical operation of the system, since it is only an educational example.

In the future, the server part could be deployed to a dedicated machine. Several clients could then access the server via the internet.

![deployment-driven-decomposition-RT](diagrams/deployment-driven-decomposition-RT.drawio.png)

### 4.7. Technologies

The choice of technologies is cross-cutting concept and addresses certain drivers. Thus, we describe it here in a similar way as the quality concepts in the next chapter.

#### 4.7.1. Architecture drivers

The choice of technologies addresses the drivers _C2_, _C4_, _G2_, _Q.Comprehensibility_, _Q.Performance.Threads_, _Q.Size_

#### 4.7.2. Solution idea

![df](diagrams/systems-technology-selection-RT.drawio.png)

Regarding the backend part, we have chosen the following Java libraries:

- NanoHttpd, a simple HTTP server,
- Jackson, a JSON (de-)serialization library,
- okhttp, a REST client.

#### 4.7.3. Design decisions

We use

- Java since the WIN students are familiar with is,
- WeatherBit and mensa-kl.de since they are free to use (at least for the amount of calls we need in this project),
- NanoHttpd and implement the REST backend ourselves since it is very lightweight and offers the students the possibility to fully comprehend how REST requests can be handled with Java and
- Jackson for JSON (de-)serialization and okhttp as REST client since these libraries are widely used, well documented and comparatively easy to understand.

#### 4.7.4. Discarded alternatives

We do not use Spring Boot since it drastically increases learning curve and deployment size.

## 5. Quality concepts

When designing a system, there are many cross-cutting design decisions that affect the system as a whole. These decisions address certain architecture drivers form solution concepts which are described in the following sections.

### 5.1. Testability concept

#### 5.1.1. Architecture drivers

_Q.Testability.Offline_, _Q.Testability.Weather_

#### 5.1.2. Solution Idea

We need a mechanism that makes it easy to exchange the real weather and menu service with services that are adequate for offline testing and for using fake weather data. For the system with the real service, a service factory facilitates the service instantiation.

The following figure illustrates these two concepts:

![dependency injection and service factory](diagrams/implementation-di-factory-DT.drawio.png)

Note that for every service, there is an interface which can be implemented by a mock or fake service. All services get their dependencies in the constructor. This way, fake or mock services can be injected for testing purpose.

#### 5.1.3. Design decisions

Dependency injection is used for the three main services. The MealController (REST controller) uses the service from the service factory which currently returns the real (production) services. Thus, with the current concept, the REST controller cannot be tested with mock service. This is ok, since the drivers do not require testability on system or integration test level. If this is required in the future, different service factories (test, production) can be introduced.

#### 5.1.4. Discarded alternatives

In every service, one could read a system environment variable to switch between different service implementations. This approach, however, is prone to errors and less flexible, since one cannot easily run tests in parallel that use different service implementations.

### 5.2. Caching concept

#### 5.2.1. Architecture drivers

Main driver: _Q.Performance.Response_, i.e. a response time of &le; 200ms.

Related drivers: _Q.Size_ and _Q.Comprehensibility_.

#### 5.2.2. Solution idea

We introduce an in-memory cache such that meals and weather data is only queried every 30 minutes.

![caching-uml](diagrams/implementation-cache-di-factory-DT.drawio.png)

The caching services act as bridges to the actual services.

The following diagram describes the behavior of the system when no data has been cached yet.

![cache-miss](diagrams/behavior-cache-miss-RT.drawio.png)

When cached data is available and not older than 30 minutes, data from the cache is used:

![cache-hit](diagrams/behavior-cache-hit-RT.drawio.png)

#### 5.2.3. Design decisions

Since weather and meal data do not change very frequently, we can cache them for at least 30 minutes. Furthermore, a simple, self-written solution is easier to comprehend for less experienced developers (cf. driver _Q.Comprehensibility_).

#### 5.2.4. Discarded alternatives

Other caching options include file system or database cache. This is discarded, since it makes the system much more complex. Also, the amount of data to be cached is very small and we only have one instance of the server running.

A typical, ready-to-use in-memory cache solution is [Ehcache](https://www.ehcache.org/). However, an inclusion of this library would increase the deployment artifact size with an additional 1.7 MB such that the requirements of driver _Q.Size_ will not be met anymore. Furthermore, it makes the code less easy to understand (cf. driver _Q.Comprehensibility_).

## 6. Risks and technical debt

It is assumed that the system is restarted at least once a month since, regarding the caching concept, cached data is held in memory forever which can result into extended memory usage when running the system for a longer time without restarting.

## 7. Outlook and future plans

In the future, server deployment as described in [4.6. Deployment and Operation](#46-deployment-and-operation), figure _Deployment-driven decomposition into clients and server_ could be made possible by adding build scripts and, optionally, also a docker file.

Furthermore, a frontend implementation with technologies that WIN students are familiar with would be a useful addition to this example (also documentation-wise).

## 8. Glossary

_cold bowl_: A cold bowl consist of fruit pieces, fruit juice and ice (and some more secret ingredients). This is a literal translation of the German word "Kaltschale".

_HTWG_: University of applied science in Konstanz, Germany.

_REST_: REpresential State Transfer, a commonly used web service design approach.

_Software-Architektur_: German for software architecture.

_WIN_: German abbreviation of the _Wirtschaftsinformatik_ study programm at HTWG. It means _business information technology_ in English - a course of studies that combines elements of computer science with business administration.
