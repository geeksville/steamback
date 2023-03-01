# Unformatted / not useful to others

THIS IS (currently) a mostly unformatted set of notes.  If you aren't the dev for this project you probably don.t want it.

react-devtools --no-sandbox

## desktop todo

option to scan and list supported games
option to scan and backup all games
option to scan and backup a particular game (for inserting into launch options)
options to poll ps to watch for games starting/exiting.

gui in tk https://stackoverflow.com/questions/24656138/python-tkinter-attach-scrollbar-to-listbox-as-opposed-to-window

use async tkinker https://pypi.org/project/async-tkinter-loop/

## JS todo

fix game infos
        # force int type, javascript comes across as strs
        # game_id = int(game_id)
		
complete change to game_info
cache game infos in python settings

* add an icon for the plugin

```
f = await window.SteamClient.InstallFolder.GetInstallFolders()
f[0].vecApps
(21) [{…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}]
0: {nAppID: 228980, strAppName: "Steamworks Common Redistributables", strSortAs: "Steamworks Common Redistributables", rtLastPlayed: 0, strUsedSize: "431262009", …}
1: {nAppID: 242760, strAppName: "The Forest", strSortAs: "Forest", rtLastPlayed: 1674017593, strUsedSize: "6227339163", …}
2: {nAppID: 268500, strAppName: "XCOM 2", strSortAs: "XCOM 2", rtLastPlayed: 1671555040, strUsedSize: "81202389052", …}
3: {nAppID: 361420, strAppName: "ASTRONEER", strSortAs: "ASTRONEER", rtLastPlayed: 1674682555, strUsedSize: "3517627893", …}
4: {nAppID: 377160, strAppName: "Fallout 4", strSortAs: "Fallout 4", rtLastPlayed: 1673104710, strUsedSize: "38354385679", …}
5: {nAppID: 459220, strAppName: "Halo Wars: Definitive Edition", strSortAs: "Halo Wars: Definitive Edition", rtLastPlayed: 1674343201, strUsedSize: "10495915939", …}
6: {nAppID: 648800, strAppName: "Raft", strSortAs: "Raft", rtLastPlayed: 1676830684, strUsedSize: "7544270164", …}
7: {nAppID: 848450, strAppName: "Subnautica: Below Zero", strSortAs: "Subnautica: Below Zero", rtLastPlayed: 1675371898, strUsedSize: "8890696147", …}
8: {nAppID: 892970, strAppName: "Valheim", strSortAs: "Valheim", rtLastPlayed: 1676826183, strUsedSize: "1620346213", …}
9: {nAppID: 962130, strAppName: "Grounded", strSortAs: "Grounded", rtLastPlayed: 1674689871, strUsedSize: "11218364509", …}
10: {nAppID: 1046030, strAppName: "ISLANDERS", strSortAs: "ISLANDERS", rtLastPlayed: 1674601452, strUsedSize: "639696154", …}
11: {nAppID: 1062090, strAppName: "Timberborn", strSortAs: "Timberborn", rtLastPlayed: 1674613249, strUsedSize: "2738071563", …}
12: {nAppID: 1070560, strAppName: "Steam Linux Runtime", strSortAs: "Steam Linux Runtime", rtLastPlayed: 1656989998, strUsedSize: "12612", …}
13: {nAppID: 1161040, strAppName: "Proton BattlEye Runtime", strSortAs: "Proton BattlEye Runtime", rtLastPlayed: 1663125166, strUsedSize: "5750336", …}
14: {nAppID: 1324130, strAppName: "Stranded: Alien Dawn", strSortAs: "Stranded: Alien Dawn", rtLastPlayed: 1674766708, strUsedSize: "9430415033", …}
15: {nAppID: 1391110, strAppName: "Steam Linux Runtime - Soldier", strSortAs: "Steam Linux Runtime - Soldier", rtLastPlayed: 1656990418, strUsedSize: "641113678", …}
16: {nAppID: 1493710, strAppName: "Proton Experimental", strSortAs: "Proton Experimental", rtLastPlayed: 1663819928, strUsedSize: "1086542197", …}
17: {nAppID: 1850570, strAppName: "DEATH STRANDING DIRECTOR'S CUT", strSortAs: "DEATH STRANDING DIRECTOR'S CUT", rtLastPlayed: 1672891913, strUsedSize: "80489531057", …}
18: {nAppID: 1887720, strAppName: "Proton 7.0", strSortAs: "Proton 7.0", rtLastPlayed: 1656992323, strUsedSize: "1098535663", …}
19: {nAppID: 2101520, strAppName: "Exogate Initiative Demo", strSortAs: "Exogate Initiative Demo", rtLastPlayed: 1676313859, strUsedSize: "2347367620", …}
20: {nAppID: 2230260, strAppName: "Proton Next", strSortAs: "Proton Next", rtLastPlayed: 1669912399, strUsedSize: "1098535663", …}
length: 21
__proto__: Array(0)


appStore.GetAppOverviewByAppID(268500)
b {appid: 268500, shortcut_override_appid: undefined, display_name: "XCOM 2", app_type: 1, mru_index: undefined, …}
app_type: 1
appid: 268500
association: (7) [{…}, {…}, {…}, {…}, {…}, {…}, {…}]
canonicalAppType: 1
controller_support: undefined
display_name: "XCOM 2"
header_filename: undefined
icon_data: undefined
icon_data_format: undefined
icon_hash: "f275aeb0b1b947262810569356a199848c643754"
library_capsule_filename: undefined
library_id: undefined
local_per_client_data: {clientid: "0", client_name: "This machine", display_status: 11, status_percentage: 100, installed: true, …}
m_gameid: undefined
m_setStoreCategories: Set(7) {2, 22, 29, 30, 23, …}
m_setStoreTags: Set(20) {9, 1677, 1741, 1708, 14139, …}
mastersub_appid: undefined
mastersub_includedwith_logo: undefined
metacritic_score: 88
minutes_playtime_forever: 331
minutes_playtime_last_two_weeks: 1
most_available_clientid: "0"
most_available_per_client_data: {clientid: "0", client_name: "This machine", display_status: 11, status_percentage: 100, installed: true, …}
mru_index: undefined
optional_parent_app_id: undefined
owner_account_id: undefined
per_client_data: [{…}]
review_percentage_with_bombs: 84
review_percentage_without_bombs: 84
review_score_with_bombs: 8
review_score_without_bombs: 8
rt_custom_image_mtime: undefined
rt_last_time_locally_played: undefined
rt_last_time_played: 1671555040
rt_last_time_played_or_installed: 1671555040
rt_original_release_date: 0
rt_purchased_time: 1670713429
rt_recent_activity_time: 1671555040
rt_steam_release_date: 1454648400
rt_store_asset_mtime: 1587583797
selected_clientid: "0"
selected_per_client_data: {clientid: "0", client_name: "This machine", display_status: 11, status_percentage: 100, installed: true, …}
shortcut_override_appid: undefined
site_license_site_name: undefined
size_on_disk: "80441395840"
sort_as: "xcom 2"
steam_deck_compat_category: 2
third_party_mod: undefined
visible_in_game_list: true
vr_only: undefined
vr_supported: undefined
BHasStoreTag: (...)
active_beta: (...)
display_status: (...)
gameid: (...)
installed: (...)
is_available_on_current_platform: (...)
is_invalid_os_type: (...)
review_percentage: (...)
review_score: (...)
status_percentage: (...)
store_category: (...)
store_tag: (...)
```

##  python todo

* implement find_games - which iterates through games that also have a remotecache.vdf file.
* implement backup_game - given a game id, create a savestate from the most recent vdf snapshot.
* Make sure we handle nested files/directories properly

assume:
vdf = the vdf file json
gamedir = /home/...userdata.../accountid/gameid

if vdf.ChangeNumber is unchanged from the last backup, no change occurred.
iterate over props (except ChangeNumber and ostype).  For each prop that is an object, pull out the filename from gamedir + the prop name - copy that file.


* update restore game code to use these new style snapshots.
* add an 'undo' option to revert the most recent restore

bigpicture cde
http://192.168.86.112:8081/devtools/inspector.html?ws=192.168.86.112:8081/devtools/page/FE611252B92C8D4189D931A9A592F88E
quick access menu
http://192.168.86.112:8081/devtools/inspector.html?ws=192.168.86.112:8081/devtools/page/2BDDD3BFD3906FDC24FC8EF294D1DC58

"steam shares" has the goog stuff in window.SteamClient

http://192.168.86.112:8081/devtools/inspector.html?ws=192.168.86.112:8081/devtools/page/B06157D2759AFF83A30044CE44A52AC1

valve python docs https://github.com/ValvePython/steam

# Unformatted follows

Possibly call it "gameshot".

docs: https://wiki.deckbrew.xyz/en/plugin-dev/getting-started

Related existing project: https://github.com/metehankutlu/decky-save-manager/issues/1

Look into https://github.com/mtkennerly/ludusavi.

https://www.jetbrains.com/lp/compose-mpp/

https://partner.steamgames.com/doc/features/cloud

decky info:
https://wiki.deckbrew.xyz/en/user-guide/home#plugin-development

```
my account ID seems to be x
valheim app id is 892970

 find /home/kevinh/.steam -name  steam_autocloud.vdf 
/home/kevinh/.steam/debian-installation/steamapps/common/Subnautica/SNAppData/SavedGames/steam_autocloud.vdf
/home/kevinh/.steam/debian-installation/steamapps/common/Steam Controller Configs/49847735/config/steam_autocloud.vdf
/home/kevinh/.steam/debian-installation/steamapps/compatdata/892970/pfx/drive_c/users/steamuser/AppData/LocalLow/IronGate/Valheim/worlds/steam_autocloud.vdf
/home/kevinh/.steam/debian-installation/steamapps/compatdata/892970/pfx/drive_c/users/steamuser/AppData/LocalLow/IronGate/Valheim/characters/steam_autocloud.vdf
/home/kevinh/.steam/debian-installation/steamapps/compatdata/1450900/pfx/drive_c/users/steamuser/Local Settings/Application Data/Desynced/Saved/SaveGames/steam_autocloud.vdf
/home/kevinh/.steam/debian-installation/steamapps/compatdata/648800/pfx/drive_c/users/steamuser/AppData/LocalLow/Redbeet Interactive/Raft/User/User_76561198010113463/steam_autocloud.vdf

ls /home/kevinh/.steam/debian-installation/userdata/49847735/892970/remote/
characters  worlds

ls /home/kevinh/.steam/debian-installation/steamapps/common/Subnautica/SNAppData/SavedGames/
options  slot0000  steam_autocloud.vdf


on steamdeck:
./.local/share/Steam/userdata/49847735/1954200/remotecache.vdf
./.local/share/Steam/userdata/49847735/1062090/remotecache.vdf
./.local/share/Steam/userdata/49847735/933820/remotecache.vdf
./.local/share/Steam/userdata/49847735/206440/remotecache.vdf
./.local/share/Steam/userdata/49847735/1324130/remotecache.vdf
./.local/share/Steam/userdata/49847735/7/remotecache.vdf
./.local/share/Steam/userdata/49847735/459220/remotecache.vdf
./.local/share/Steam/userdata/49847735/1318690/remotecache.vdf
./.local/share/Steam/userdata/49847735/848350/remotecache.vdf
./.local/share/Steam/userdata/49847735/848450/remotecache.vdf
./.local/share/Steam/userdata/49847735/815370/remotecache.vdf
./.local/share/Steam/userdata/49847735/241100/remotecache.vdf
./.local/share/Steam/userdata/49847735/1085510/remotecache.vdf
./.local/share/Steam/userdata/49847735/264710/remotecache.vdf
./.local/share/Steam/userdata/49847735/323190/remotecache.vdf
./.local/share/Steam/userdata/49847735/268500/remotecache.vdf
./.local/share/Steam/userdata/49847735/648800/remotecache.vdf
./.local/share/Steam/userdata/49847735/1046030/remotecache.vdf
./.local/share/Steam/userdata/49847735/1332010/remotecache.vdf
./.local/share/Steam/userdata/49847735/892970/remotecache.vdf
./.local/share/Steam/userdata/49847735/377160/remotecache.vdf
./.local/share/Steam/userdata/49847735/1127400/remotecache.vdf
./.local/share/Steam/userdata/49847735/242760/remotecache.vdf
./.local/share/Steam/userdata/49847735/962130/remotecache.vdf
./.local/share/Steam/userdata/49847735/548430/remotecache.vdf
./.local/share/Steam/userdata/49847735/1284190/remotecache.vdf
./.local/share/Steam/userdata/49847735/1794680/remotecache.vdf
./.local/share/Steam/userdata/49847735/1850570/remotecache.vdf
./.local/share/Steam/userdata/49847735/620/remotecache.vdf
./.local/share/Steam/userdata/49847735/361420/remotecache.vdf

all vdf files inside of userdata
/home/kevinh/.steam/debian-installation/userdata/49847735/250820/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/848450/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/264710/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/1332010/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/750920/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/275850/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/1127400/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/1954200/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/268500/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/361420/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/602320/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/892970/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/323190/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/1318690/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/config/serverbrowser_ui.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/config/localconfig.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/config/compat.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/config/shortcuts.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/config/controller_configs/apps/892970/DS88034c83e217/49847735/2916630005/controller_configuration.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/548430/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/7/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/7/remote/sharedconfig.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/718850/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/242760/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/1594320/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/1794680/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/427520/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/933820/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/ugc/consumed.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/ugc/241100_subscriptions.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/1085510/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/377160/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/870780/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/1324130/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/962130/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/648800/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/848350/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/760/screenshots.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/241100/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/241100/remote/2916630005_controller_config.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/206440/remotecache.vdf
/home/kevinh/.steam/debian-installation/userdata/49847735/200510/remotecache.vdf
```

Plan:
Find apps based on remotecache.vdf
Look for changes to remote rc.vdf, if file has changed, look for changes to "localtime" on the files.  If that changed record a new "versioned" backup event for that set of files.  Copy the files away

For restore, let user pick from versioned backups.

Run scan after each game exit (FIXME - how to hook this?)
Work on both desktop linux or steamdeck.

subnautica:
less /home/kevinh/.steam/debian-installation/userdata/49847735/264710/remotecache.vdf


sample from xcom2:

```
kevinh@kdesktop:~/3dprinting$ cat /home/kevinh/.steam/debian-installation/userdata/49847735/268500/remotecache.vdf
"268500"
{
	"ChangeNumber"		"-6703994677807818784"
	"ostype"		"-184"
	"my games/XCOM2/XComGame/SaveData/profile.bin"
	{
		"root"		"2"
		"size"		"15741"
		"localtime"		"1671427173"
		"time"		"1671427172"
		"remotetime"		"1671427172"
		"sha"		"df59d8d7b2f0c7ddd25e966493d61c1b107f9b7a"
		"syncstate"		"1"
		"persiststate"		"0"
		"platformstosync2"		"-1"
	}
	"my games/XCOM2/XComGame/SaveData/save1"
	{
		"root"		"2"
		"size"		"107583"
		"localtime"		"1671423668"
		"time"		"1671423667"
		"remotetime"		"1671423667"
		"sha"		"9733e89562aae1dd4af5e8364d7eaa3c2fd1315c"
		"syncstate"		"1"
		"persiststate"		"0"
		"platformstosync2"		"-1"
	}
	"my games/XCOM2/XComGame/SaveData/save2"
	{
		"root"		"2"
		"size"		"455803"
		"localtime"		"1671425486"
		"time"		"1671425485"
		"remotetime"		"1671425485"
		"sha"		"d0d64159d08e1411823f42120ff00f506ee12282"
		"syncstate"		"1"
		"persiststate"		"0"
		"platformstosync2"		"-1"
	}
	"my games/XCOM2/XComGame/SaveData/save3"
	{
		"root"		"2"
		"size"		"160191"
		"localtime"		"1671424081"
		"time"		"1671424080"
		"remotetime"		"1671424080"
		"sha"		"b0860b4940024abb8a332762d9d9915adeae0d70"
		"syncstate"		"1"
		"persiststate"		"0"
		"platformstosync2"		"-1"
	}
	"my games/XCOM2/XComGame/SaveData/save4"
	{
		"root"		"2"
		"size"		"658989"
		"localtime"		"1671426050"
		"time"		"1671426049"
		"remotetime"		"1671426049"
		"sha"		"ed0f1c3fb92154ca439cdb56d7f29319d86bee19"
		"syncstate"		"1"
		"persiststate"		"0"
		"platformstosync2"		"-1"
	}
	"my games/XCOM2/XComGame/SaveData/save5"
	{
		"root"		"2"
		"size"		"999847"
		"localtime"		"1671426375"
		"time"		"1671426374"
		"remotetime"		"1671426374"
		"sha"		"688c5447e23b09d7460c57c7b032c84f326d24c9"
		"syncstate"		"1"
		"persiststate"		"0"
		"platformstosync2"		"-1"
	}
	"my games/XCOM2/XComGame/SaveData/save6"
	{
		"root"		"2"
		"size"		"215980"
		"localtime"		"1671427173"
		"time"		"1671427172"
		"remotetime"		"1671427172"
		"sha"		"4576b983dea60ed34eb178a2b808f0737fe181ed"
		"syncstate"		"1"
		"persiststate"		"0"
		"platformstosync2"		"-1"
	}
}
```

(base) kevinh@kdesktop:~/3dprinting$ 

Web api to get app info (including name)
https://store.steampowered.com/api/appdetails?appids=892970

Local filesystem seems to be in:

/home/kevinh/.steam/debian-installation/steamapps/appmanifest_892970.acf

Hi,

I'm a sw dev who has really been loving my Steam Deck.  And though I like the steam cloud based backups for game saves, one particular game of mine (Valheim heh) really makes me wish I had some sort of automatic 'versioned' backups of game saves.  So that I could easily go back to an old save (even when the game doesn't provide such a feature).  

For now I've made a couple of nasty scripts for the game I most wanted this for but I have two questions for ya'll:

* Would a nice GUI based app (or decky loader plugin) that "lets you reload from any of your recent saves" be useful?
* Has anyone else already made such an app?  If so - I'd eagerly just use that instead! My googling thus far has failed though...

I've looked into the Steam backup API docs and explored around on the filesystem and I think I can make a nice mechanism that automatically works for all Steam cloud backup based games.  For games that are not steam cloud backup based I'll have a mechanism so that people can add those on their own if they wish.

Any feedback or pointers would be appreciated!

---

Hi decky geeks!
I've used decky and think it is slick.  I'm now investigating making a decky plug-in to provide 'roll-back' save/restore for games that use steam-cloud backups (initially, possibly other games later).  I've read the Steam
docs and looked at remotecache.vdf files on my steamdeck and I think I can make a pretty friendly & safe tool for novice users.

I've written a fair amount of JS and python stuff but I do have some questions on decky.  Any feedback or pointers would be appreciated:

* Does decky already provide the appid to name mappings for games somewhere? I could scrape ...steam/debian-installation/steamapps/appmanifest_*.vcf but I assume this has been needed already and I wouldn't want to scrape again.  If you don't already have such a service, would you like me to send this in as a PR somehow or would you rather me just leave it in my plugin.
* Does decky have any hooks/callbacks/whatever I can use to be notified when an app has been launched/exited from the Steam UI?
* I assume for my 'backend' of my plugin I should write it in python because that's the preferred backend language in decky land?
* How do you develop/test your decky plugins?  Is it possible to run plugins on my linux desktop in Steam big-picture mode?

Rough write-up on what I'm considering: https://www.reddit.com/r/SteamDeck/comments/112awgm/id_like_to_make_a_steam_deck_app_to_let_you/


decky replies:


AAGaming says:
 Does decky already provide the appid to name mappings for games somewhere? 
appStore global
Does decky have any hooks/callbacks/whatever
various Register* functions in SteamClient. they return an object {unregister: f ()} which you MUST store and later call in your plugin's onDismount to prevent major issues when your plugin is updated

ok coolbeans - I'll look in the SteamClient code to see if someone already has the remotecache stuff.  If not there I'll try to add something that fits nicely. 
SteamClient is an interface created from native steam client code
we only have the interface itself, cant view its source code
look at our existing typings for it at https://github.com/SteamDeckHomebrew/decky-frontend-lib/blob/main/src/deck-components/SteamClient.ts and browse it by evaluating it in the Console tab of the CEF DevTools 


