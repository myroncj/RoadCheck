from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
import json
import requests
#from requestURL import requestURL
import gmplot
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize
from sklearn.cluster import DBSCAN


# Create your views here.

def show(request):
    name = "Myron CJ"
    return HttpResponse("My Name is " + str(name))

def showMap(request):
    print(" --- Fetching Data --- ")
    #r = requestURL()  # gets API response
    response = requests.get("https://firestore.googleapis.com/v1beta1/projects/anomalycheck-ce6c1/databases/(default)/documents/Anomalies/AnomalyDetails/AnomalyList?orderBy=TimeStamp&pageSize=10000")
    json_data = json.loads(response.content)
    print(" --- Data Fetched --- ")
    i = 0  # item count
    one = []  # list to hold latitude and longitude

    print(" --- Processing Data --- ")

    for item in json_data['documents']:
        imp = item['fields']['Impact']['doubleValue']
        lng = item['fields']['Longitude']['doubleValue']
        lat = item['fields']['Latitude']['doubleValue']
        ct = item['createTime']

        one.append((lat, lng))

        i += 1

    print(" --- " + str(i) + " items fetched and processed --- ")

    print(" --- Creating the Map --- ")

    # sets the initial location to show on the map
    # in this case it's Bengaluru
    gmap = gmplot.GoogleMapPlotter(12.932944, 77.605767, 18)

    top_attraction_lats, top_attraction_lons = zip(*one)  # scatter points

    print(" --- Plotting scatter points --- ")

    gmap.scatter(top_attraction_lats, top_attraction_lons, '#000000', size=3, marker=False)

    gmap.draw("templates/myMap.html")  # draws the scatter points on the map and creates the webpage

    print(" --- The Map is ready --- ")

    y = json_normalize(json_data['documents'])  # Very Important Function

    #print(json_data['documents'])

    # print(y)

    # X = y.iloc[:, [1, 2, 3, 4]].values
    X = y.iloc[:, [2, 3]].values

    print("\n --- Before preprocessing --- ")
    print(X)

    ct = 0
    for loc in X:
        if int(loc[0]) == 0 and int(loc[1]) == 0:
            X = np.delete(X, ct, 0)
        # print(str(ct) + " removed")
        else:
            # print(str(loc[0]) + " " + str(loc[1]))
            ct += 1

    print("\n --- Count :" + str(ct) + " --- ")
    print("\n --- After preprocessing --- ")
    print(X)

    db = DBSCAN(eps=2.0 / 6371, min_samples=10).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    components = db.components_
    indices = db.core_sample_indices_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    print('\n --- Estimated number of clusters %d --- ' % n_clusters_)
    print("\n --- Labels --- \n" + str(labels))
    print("\n --- Components --- \n" + str(components))
    print("\n --- Indices --- \n" + str(indices))
    print("\n --- Count :" + str(ct) + " --- ")

    # Plot result
    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each)
              for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = (labels == k)

        xy = X[class_member_mask & core_samples_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)

        xy = X[class_member_mask & ~core_samples_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)

    plt.title('Estimated number of clusters: %d' % n_clusters_)
    #plt.show()  # uncomment to see the cluster plot
    return render_to_response('myMap.html')
