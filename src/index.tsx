import {
  ButtonItem,
  definePlugin,
  // Menu, MenuItem, showContextMenu,
  PanelSection,
  PanelSectionRow,
  ServerAPI,
  staticClasses,
  LifetimeNotification,
  showModal,
  ConfirmModal,
  Navigation,
  AppOverview,
  Router
} from "decky-frontend-lib"
import { VFC, useState, useEffect } from "react"
import { FiDownload, FiUpload } from "react-icons/fi"
import SteamID from "steamid"
import TimeAgo from "javascript-time-ago"
import en from "javascript-time-ago/locale/en"


// FIXME - find a better source for these defs?, I'm hand specifying here
// based on looking at ProtonDB plugin
declare let App: any // used for m_currentUser

declare namespace appStore {
  function GetAppOverviewByGameID(appId: number): AppOverview
}

/**
 * Used to provide context to do_backup
 */
interface GameInfo {
  game_id: number
  game_name: string // The display name for this game (required by python install directory search)
  install_root: string // where the files are installed.  Normally from SteamClient.InstallFolder.GetInstallFolders()
  save_games_root?: string // only populated by python, optional when generated in javascript
}

/**
 * A result object from do_backup or get_saveinfos
 */
interface SaveInfo {
  game_info: GameInfo
  timestamp: number
  filename: string
  is_undo: boolean
}


let gServerAPI: ServerAPI | undefined = undefined
let gRunningGameInfo = undefined as GameInfo | undefined

// Find the currently mounted game filesystems
async function getMounted() {
  const folders = await SteamClient.InstallFolder.GetInstallFolders() as any[]

  //console.log("folder dirs", folders)
  const r = await gServerAPI!.callPluginMethod("find_mounted", {
    dirs: folders.map(f => f.strFolderPath)
  })

  if(!r.success) throw new Error('find_mounted failed')
  const mounted = r.result as string[]

  const filteredFolders = folders.filter(f => mounted.includes(f.strFolderPath))
  //console.log("filtered dirs", filteredFolders)

  return filteredFolders
}

/**
 * Generate a game_info object (which includes install_root) for the given game_id, or throw if not found
 * @param game_id 
 * @returns 
 */
async function makeGameInfo(game_id: number): Promise<GameInfo> {
  const folders = await getMounted()
  for (let f of folders) {
    const appIds = new Set<number>(f.vecApps.map((a: any) => a.nAppID))
    //console.log("app set vs ", f.vecApps, f.strFolderPath, appIds, game_id)
    if (appIds.has(game_id)) {
      const info: GameInfo = {
        game_id: game_id,
        game_name: appStore.GetAppOverviewByGameID(game_id).display_name,
        install_root: f.strFolderPath
      }
      return info
    }
  }
  throw new Error(`game_info not found for ${game_id}`)
}  

async function doBackup(gameInfo: GameInfo) {
  // we check when the game is launched _or_ landed because steam cloud might have updated it from some other PC      
  try {
    console.log("Steamback backup game: ", gameInfo)
    const r = await gServerAPI!.callPluginMethod("do_backup", {
      game_info: gameInfo,
      dry_run: false
    })

    if(!r.success)
      throw new Error('do_backup failed')

    const saveinfo = r.result as SaveInfo
    console.log("steamback backup results", saveinfo)
    if (saveinfo)
      gServerAPI!.toaster.toast({
        title: 'Steamback',
        body: `${gameInfo.game_name} snapshot taken`,
        icon: <FiDownload />,
      });
  }
  catch (error: any) {
    console.error('Steamback backup', error)
  }
}

const SteambackContent: VFC<{ serverAPI: ServerAPI }> = ({ serverAPI }) => {
  const [saveInfos, setSaveInfos] = useState<SaveInfo[]>([])
  const [supportedGameInfos, setSupportedGameInfos] = useState<GameInfo[] | undefined>(undefined)
  const [dryRunGameInfo, setDryRunGameInfo] = useState<GameInfo | undefined>(undefined)

  // Create formatter (English).
  const timeAgo = new TimeAgo('en-US')

  // Find which games we can work on
  async function getSupported() {
    const folders = await getMounted()
    let gameInfos: GameInfo[] = []
    for (let f of folders) {
      for (let a of f.vecApps) {
        const info: GameInfo = {
          game_id: a.nAppID,
          game_name: appStore.GetAppOverviewByGameID(a.nAppID).display_name,
          install_root: f.strFolderPath
        }
        //console.log("steamback considering", f)
        gameInfos = gameInfos.concat(info)
      }
    }

    //console.log("installed apps", gameInfos)
    const r = await serverAPI.callPluginMethod("find_supported", {
      game_infos: gameInfos
    })

    let supported = r.result as GameInfo[]
    //console.log("steamback supported", r.result)
    supported.sort((a, b) => a.game_name.localeCompare(b.game_name)) // sort by name
    setSupportedGameInfos(supported)
  }

  // Get the list of save games
  async function getSaveInfos() {
    serverAPI.callPluginMethod("get_saveinfos", {}).then(saveinfo => {
      // console.log("steamback saveinfos", saveinfo.result)
      setSaveInfos(saveinfo.result as SaveInfo[])
    }).catch(e => {
      console.error("steamback saveinfos failed", e)
    })
  }

  // Get the info for the currently running game (if it could be saved now)
  async function getSaveNow() {
    if(gRunningGameInfo !== undefined) {
      const gameInfo = gRunningGameInfo
      console.log("Checking running save info: ", gameInfo)
      serverAPI.callPluginMethod("do_backup", {
        game_info: gameInfo,
        dry_run: true
      }).then(saveinfo => {
        console.log("steamback dry run result", saveinfo.result)
        setDryRunGameInfo(saveinfo.result ? gameInfo : undefined)
      }).catch(e => {
        console.error("steamback dryrun failed", e)
      })
    }
  }

  useEffect(() => {
    getSupported()
    getSaveInfos()
    getSaveNow()
  }, []) // extra [] at end means only run for first render

  // Show a button to backup the currently running game
  function getRunningBackupHtml(): JSX.Element {
    if(dryRunGameInfo === undefined)
      return <div></div>

    const gameInfo = dryRunGameInfo!

    async function doBackupNow() {
      await doBackup(gameInfo)
      setSaveInfos(saveInfos) // force a redraw of the saveinfo GUI list
      setDryRunGameInfo(undefined) // we just did a save so until things change we can't do another
    }

    const buttonText = "Backup now"
    const labelText = gameInfo.game_name
    const descText = "Attempts to backup the currently running game"
    return <PanelSectionRow>
        <ButtonItem onClick={doBackupNow}
          icon={<FiDownload />}
          description={descText}
          label={labelText}>
          {buttonText}
        </ButtonItem>
      </PanelSectionRow>  
  }


  /// Only show snapshot section if we have some saveinfos
  // removed alpha disclaimer: <span style={{ padding: '1rem', display: 'block' }}>This plugin is currently in <b>alpha</b> testing, if you see problems use the 'Undo' button and let us know.  </span>
  const snapshotHtml = saveInfos.length < 1 ?
    <div></div> :
    <PanelSection title="Snapshots">
      {
        saveInfos.map(si => {
          // console.log('showing saveinfo ', si)

          const agoStr = timeAgo.format(new Date(si.timestamp))

          const doRestore = () => {
            console.info('Doing steamback restore', si)
            serverAPI.callPluginMethod("do_restore", {
              save_info: si
            }).then(() => {
              serverAPI.toaster.toast({
                title: 'Steamback',
                body: `Reverted ${si.game_info.game_name} from snapshot`,
                icon: <FiUpload />,
              })
              Navigation.Navigate(`/library/app/${si.game_info.game_id}`)
            }).catch(error =>
              console.error('Steamback restore', error)
            )
          }

          // raise a modal dialog to confirm the user wants to restore
          function askRestore() {
            const title = si.is_undo ? "Revert recent snapshot" : "Revert to snapshot"
            const message = si.is_undo ?
              `Are you sure you want to undo your changes to ${si.game_info.game_name}?` :
              `Are you sure you want to revert ${si.game_info.game_name} to the save from ${agoStr}?`

            Navigation.CloseSideMenus() // close decky UI (user will see notification when restore completes)
            showModal(
              <ConfirmModal
                onOK={doRestore}
                strTitle={title}
                strDescription={message}
              />, window
            )
          }

          const runningApps = new Set(Router.RunningApps.map(a => parseInt(a.appid)))
          // console.log("running apps", runningApps, si.game_id, runningApps.has(si.game_id))
          const buttonText = si.is_undo ? `Undo` : `Revert`
          const labelText = si.game_info.game_name
          const descText = si.is_undo ? `Reverts recent Steamback changes` : `Snapshot from ${agoStr}`
          // bottomSeparator="none" label="some label" layout="below"
          return <PanelSectionRow>
            <ButtonItem onClick={askRestore}
              icon={<FiUpload />}
              disabled={runningApps.has(si.game_info.game_id)} // Don't let user restore files while game is running
              description={descText}
              label={labelText}>
              {buttonText}
            </ButtonItem>
          </PanelSectionRow>
        })
      }
    </PanelSection>

  const supportedHtml = supportedGameInfos === undefined ?
    <span style={{ padding: '1rem', display: 'block' }}>Finding supported games...</span> :
    <ul style={{ listStyleType: 'none', padding: '1rem' }}>
      {
        supportedGameInfos.map(info => {
          // console.log('showing supported ', info)

          return <li style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', paddingBottom: '10px', width: '100%', justifyContent: 'space-between' }}>
            <span>{info.game_name}</span>
          </li>
        })
      }
    </ul>

  const helpUrl = "https://github.com/geeksville/steamback/blob/main/README.md"
  return (
    <div>
      <span style={{ padding: '1rem', display: 'block' }}><a href={helpUrl} onClick={async () => {
        Navigation.CloseSideMenus()
        Navigation.NavigateToExternalWeb(
          `${helpUrl}`
        )
      }}>Steamback</a> automatically makes save-game snapshots for many Steam games. See our github page for more information.</span>

      {getRunningBackupHtml()}
      {snapshotHtml}

      <PanelSection title="Supported games">
        {supportedHtml}
      </PanelSection>
    </div>
  )
}


export default definePlugin((serverApi: ServerAPI) => {

  //console.info('IN STEAMBACK!')

  TimeAgo.addDefaultLocale(en)
  gServerAPI = serverApi

  const taskHook = SteamClient.GameSessions.RegisterForAppLifetimeNotifications(async (n: LifetimeNotification) => {
    console.log("Steamback AppLifetimeNotification", n);

    const gameInfo: GameInfo = await makeGameInfo(n.unAppID)

    // Update the global that the GUI uses for 'backup now' button
    gRunningGameInfo = n.bRunning ? gameInfo : undefined 
    return doBackup(gameInfo)
  })

  let sid = new SteamID(App.m_CurrentUser.strSteamID)

  // console.debug(`Setting steamback account id ${sid.accountid}`)
  serverApi.callPluginMethod("set_account_id", {
    id_num: sid.accountid
  }).catch(e =>
    console.error("Can't set steamback account", e)
  )

  return {
    title: <div className={staticClasses.Title}>Steamback</div>,
    content: <SteambackContent serverAPI={serverApi} />,
    icon: <FiDownload />,
    onDismount() {
      taskHook!.unregister()
    },
  }
})
