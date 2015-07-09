import matplotlib
# headless server, use backend with display
matplotlib.use('Agg')
import pylab
import pprint
import json
import datetime
import matplotlib.dates as mdates
import numpy

def init_month():
    # initialize new data structure for month and return it
    data ={}
    for language in get_languages():
        data[language] = 0
    return data
 
def get_languages():
    languages = []
    with open("languages.json") as fi:
        data = json.loads(fi.read())
        for item in data:
            languages.append(item['name'])
    return languages
 
def get_data():
    # read the core data and return it
    with open("results.txt") as fi:
        data = eval(fi.read())
    return data

def build_data():

    # init
    month_data = []
    this_month = None
    monthly_totals = {}
    key = (0, 0)
    start_year = 2010
    

    # month_data: [{'date': {'language': score, 'language': score}}, ...]
    for item in get_data():
        for date, values in item.items():
            day, month, year = eval(date)
            if year < start_year:
                break

            if month != key[0]:
                # we have reached a month boundary
                if this_month:
                    # (ignore initial empty month)
                    if monthly_totals[key] == 0:
                        print("empty month: %s" % str(key))
                    # save current month
                    #print("saving %s" % this_month)
                    month_data.append({key: this_month})
                # init new month
                key = (month, year)
                this_month = init_month()
                #print("init %s" % str(key))
                monthly_totals[key] = 0
            
            for language, score in values.items():
                # add this day to monthly totals
                #print("%s: %s" % (language, score))
                this_month[language] += score
                # keep track of monthly total
                monthly_totals[key] += score

    # by_language: {'language': {'date': [date, date,..], 'ratio': [ratio, ratio, ...], 'score': [score, score]}}
    by_language = {}
    for language in get_languages():
        by_language[language] = {'date': [], 'ratio': [], 'score': [], 'total': 0}

    for info in month_data:
        for date, scores in info.items():
            for language, score in scores.items():
                month, year = date
                date_obj = datetime.date(year, month, 15)
                # get ratios
                if monthly_totals[date] != 0:
                    ratio = float(score) / float(monthly_totals[date])
                    by_language[language]['ratio'].append(ratio)
                    by_language[language]['date'].append(date_obj)
                    by_language[language]['total'] += score   
                    by_language[language]['score'].append(score)
 

    pprint.pprint(by_language)

    exclude = ['c']
    contenders = []
    for language, data in by_language.items():
        if language in exclude:
            continue
        if not contenders:
            contenders.append(language)
        else:
            score = data['total']
            for i, contender in enumerate(contenders):
                if score > by_language[contender]['total']:
                    print("inserting %s at position %s" % (language, i))
                    contenders.insert(i, language)
                    break

    contenders = contenders[0:5]
    print("Final list: %s" % contenders)


    colormap = pylab.cm.gist_ncar
    pylab.gca().set_color_cycle([colormap(i) for i in numpy.linspace(0, 0.9, len(contenders))])

    years    = mdates.YearLocator()   # every year

    fig, ax = pylab.subplots()
    ax.xaxis.set_major_locator(years)
    for language in contenders:
        data = by_language[language]
        ax.plot(data['date'], data['ratio'], '-', label=language)
        ax.legend(ncol=1, loc='upper left', fontsize='x-small')
    pylab.savefig('ratio.png')

    fig, ax = pylab.subplots()
    ax.xaxis.set_major_locator(years)
    for language in contenders:
        data = by_language[language]
        ax.plot(data['date'], data['score'], '-', label=language)
        ax.legend(ncol=1, loc='upper left', fontsize='x-small')
    pylab.savefig('score.png')



if __name__ == "__main__":
    build_data()
