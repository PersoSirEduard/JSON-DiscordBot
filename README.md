# JSON-DiscordBot

## Description
For now this repository contains a JSON file that controls a Discord bot using the official API for Python. By fetching the JSON file from this repository, it enables the bot the perform different actions when the user mentions specific key words that have an intend from a dictionnary.
#### Features
* Respond to specific discord messages using a dictionnary of intends
* Live modification of bot actions without the need to restart the app
* Respond using lists (i.e. quotes, jokes, etc), texts, and files
* Very basic message formatting directly within the JSON file

## Modification of the `commands.json` file
This next section will summarize the commands and modifications available for the bot right now.
### Sections
The `commands.json` file is seperated into 3 main parent nodes that have a different contribution:
* `intends`
* `uniques`
* `actions`

### `intends` block
This section enables stores the intend dictionnary for the bot. Hence, words are associated with a intention or a concept (physical or emotional). Adding an intend to the list will require the intend to be a name and to contain an array of related words.
For example, a new entry would look like this:
```json
"ask": [
  "tell",
  "say",
  "give",
  "answer",
  "buy"
],
```
*Note: It is important to keep a strict JSON text format for the bot to read. If not, no action or command is going to work.*


### `uniques` block
The `uniques` section is straight forward. If a specific string of text is typed, the bot will deliver a static response.
To use it, a new entry would look like this:
```json
"uniques": {
  "guess who's back": "Back again!"
},
```
In this example, if the user types "guess who's back" in a text channel, the bot is going to reply in the same channel with "Back again!".

### `actions` block
This following section enables the bot the perform more complexe tasks. To begin with a new action, a new dictionary must be introduced in the `actions` list. The name of the new object **does not matter for now**.
Next, for the action to execute, it will need to have an array `intends` with the names of the intends from the `intends` section that we previously investigated. There is no restriction to the amount of intends the array can contain. In this manner, complexe situations can be detected by the bot if intends are set properly. **This property is required for all actions up to now.**
#### Example:
```json
"sad_response": {
  "intends": ["self", "sad"],
   ...
}
```
Another mandatory property is the `responseType` which indicates to the bot what type of response to use. For now, 2 different responses are available:
* `text`: Send text (formatted or not) with images and files
* `list`: Query a response line from a list contained within a .txt file

*Note: The order of the actions is important. Top of the list actions are first prioritized.*

#### `text` response
The `text` response type requires a `response` entry that contains a string. This string can be formatted in multiple ways:
* `$user` in the response string will the replaced by the Discord user mention of the author
* Custom variables can also be introduced in the string. They can be introduced by using `%variable-name` inside the string.

To introduce new variables, they need to be declared inside the `responseFormat` dictionary entry. For example,
```json
"i_am_joke": {
  "intends": ["self"],
  "responseType": "text",
  "responseFormat": {
    "msg": {
      "extract_after_intend": "self",
      "upper": true
      }
    },
    "response": "Hi %msg, I am dad!"
  }
```
The name of the children inside `responseFormat` define the name used for the variable when invoked inside the response string. This variable can then contain multiple arguments that are still developed:
* `extract_after_intend`: Splits the user message text from the word from an intend dictionary and keeps the latter part of the string. The name of the used intend is required as an argument.
* `extract_before_intend`: Splits the user message text from the word from an intend dictionary and keeps the former part of the string. The name of the used intend is required as an argument.
* `extract_from_intend`: Extract the specific intend word from the user message text. The name of the used intend is required as an argument.
* `extract_after_string`: Splits the user message text from a specified string and keeps the latter part of the string. The string sample is required as an argument.
* `extract_before_string`: Splits the user message text from a specified string and keeps the former part of the string. The string sample is required as an argument.
* `lower`: Lower every character from the current value of the variable. This is a boolean.
* `upper`: Capitalizes every character from the current vlaue of the variable. This is a boolean.

*Note: The order of the variable's properties is important (order is from top to bottom).*

The `text` response can also use the `file` property to send an image or a file under the limited file size offered by Discord.

Finally, the final response can be formatted inside the `response` property.

#### `list` response
The `list` response supports text files locally and online. This response type requires a `responseFile` with the name of the file containing the list. Also, this response type uses `responseChoice` to select the item from the list to be sent to the user. By default, this property has a value of `random`, but an index integer can specified for a specific line from the list.
