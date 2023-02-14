Possibly call it "gameshot".

Look into https://github.com/mtkennerly/ludusavi.

https://www.jetbrains.com/lp/compose-mpp/

https://partner.steamgames.com/doc/features/cloud

decky info:
https://wiki.deckbrew.xyz/en/user-guide/home#plugin-development

my account ID seems to be 49847735
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

Plan:
Find apps based on remotecache.vdf
Look for changes to remote rc.vdf, if file has changed, look for changes to "localtime" on the files.  If that changed record a new "versioned" backup event for that set of files.  Copy the files away

For restore, let user pick from versioned backups.

Run scan after each game exit (FIXME - how to hook this?)
Work on both desktop linux or steamdeck.

subnautica:
less /home/kevinh/.steam/debian-installation/userdata/49847735/264710/remotecache.vdf


sample from xcom2:

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




