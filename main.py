import sys
import delta

delta.config.load_config()

extract_folder = sys.argv[1]
reader = delta.utilities.xpreader(
  extract_folder,
  filenamesindexing=0
)
print(
  reader.positions,
  reader.channels,
  reader.timepoints
)

ppln = delta.pipeline.Pipeline(reader)

ppln.process()
