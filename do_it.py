from progress_of_year import YearProgress

seed = "rum://seed?v=1&e=0&n=0&cxxxxxxijpNhIaH5sa9TCLPkHCnpnROM8"
pvtkey = "0x8dxxxxx9412a"
jsonfile = "year_progress.json"
bot = YearProgress(seed, pvtkey, jsonfile, n=1)
bot.run()
