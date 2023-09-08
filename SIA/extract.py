from threading import Thread
import extractors as ext
import pandas as pd

class ThreadWithReturnValue(Thread):
    """ Allow threads to return values"""


    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
    
if __name__ == "__main__":
    
    # Create a list of the functions from the extractors.py file
    # Removed ext.bqprime_daily_extractor, due to bot blocking
    func = [ext.finex_daily_extractor, ext.et_daily_extractor, ext.eqbull_daily_extractor, ext.cnbc_daily_extractor,  ext.zee_daily_extractor, ext.business_standard_daily_extractor, ext.bt_daily_extractor]
    df = pd.DataFrame(columns=["Date", "Title", "News", "Author","Source"])
    # Create 8 threads for 8 websites
    # Each thread will extract data from one website
    threads = []
    for i in range(7):
        threads.append(ThreadWithReturnValue(target = func[i], args=(df,)))

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    
    for thread in threads:
        ds = thread.join()
        df = pd.concat([df, ds], ignore_index=True)
    
    # df = ext.finex_daily_extractor(df)
    # df = ext.et_daily_extractor(df)
    # df = ext.eqbull_daily_extractor(df)
    # df = ext.cnbc_daily_extractor(df)
    # df = ext.bqprime_daily_extractor(df)
    # df = ext.zee_daily_extractor(df)
    # df = ext.business_standard_daily_extractor(df)
    # df = ext.bt_daily_extractor(df)


    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    df.to_csv(f"articles-{today}.csv", index=False)