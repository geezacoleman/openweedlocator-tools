CONFIG_DAY_SENSITIVITY_1 = {
  "//comment_gog": "enter parameters related to green-on-green detection",
  "conf": 0.6,
  "iou": 0.7,
  "filter_id": "null",

  "//comment_gob": "parameters related to green-on-brown detection",
  "exgMin": 25,
  "exgMax": 200,
  "hueMin": 39,
  "hueMax": 83,
  "saturationMin": 50,
  "saturationMax": 220,
  "brightnessMin": 60,
  "brightnessMax": 190,
  "minArea": 10,
  "invert_hue": False,

  "//comment_general": "parameters related to general OWL operation",
  "show_display": False,
  "algorithm": "exhsv",
  "resolution": [416, 320]
}