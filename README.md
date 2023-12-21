# etoile
etoile is a project for real-time traffic analysis. It's named after [Place de l'Étoile](https://en.wikipedia.org/wiki/Place_Charles_de_Gaulle) which is a famous road junction in Paris.

## Dependencies

To install the dependencies:

```
$ pip install -r requirements.txt
```

## Additional Setup

There is some setup in order to get the demo to work.

1. Create an Ensign project on [rotational.app](https://rotational.app).

2. Create two topics in your project (`figure_updates_json` and `detection_frames`).

3. Create an API key and download the API key.

4. Find a traffic livestream or video on YouTube for the data source.

## Running the Demo

This will run the demo dashboard locally and should open it up in your web browser.

```
$ streamlit run demo.py -- -c [your-api-key.json]
```

To get data for the demo, find a YouTube livestream or video with traffic and run the publish script.

```
$ python publish.py -c creds/full-access.json -s "[YouTube URL]"
```

The dashboard should be updated in real time!