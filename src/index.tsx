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

/**
 * Generate a game_info object (which includes install_root) for the given game_id, or throw if not found
 * @param game_id 
 * @returns 
 */
async function makeGameInfo(game_id: number): Promise<GameInfo> {
  const folders = await SteamClient.InstallFolder.GetInstallFolders()
  for (let f of folders) {
    const appIds = new Set<number>(f.vecApps.map((a: any) => a.nAppID))
    // console.log("app set vs ", f.vecApps, appIds, game_id)
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

const SteambackContent: VFC<{ serverAPI: ServerAPI }> = ({ serverAPI }) => {
  const [saveInfos, setSaveInfos] = useState<SaveInfo[]>([])
  const [supportedGameInfos, setSupportedGameInfos] = useState<GameInfo[]>([])

  // Create formatter (English).
  const timeAgo = new TimeAgo('en-US')

  // Find which games we can work on
  async function getSupported() {
    const folders = await SteamClient.InstallFolder.GetInstallFolders()
    let gameInfos: GameInfo[] = []
    for (let f of folders) {
      for (let a of f.vecApps) {
        const info: GameInfo = {
          game_id: a.nAppID,
          game_name: appStore.GetAppOverviewByGameID(a.nAppID).display_name,
          install_root: f.strFolderPath
        }
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

  useEffect(() => {
    getSupported()

    serverAPI.callPluginMethod("get_saveinfos", {}).then(saveinfo => {
      // console.log("steamback saveinfos", saveinfo.result)
      setSaveInfos(saveinfo.result as SaveInfo[])
    }).catch(e => {
      console.error("steamback saveinfos failed", e)
    })
  }, []) // extra [] at end means only run for first render

  /// Only show snapshot section if we have some saveinfos
  const snapshotHtml = saveInfos.length < 1 ?
    <div></div> :
    <PanelSection title="Snapshots">
      <span style={{ padding: '1rem', display: 'block' }}>This plugin is currently in <b>alpha</b> testing, if you see problems use the 'Undo' button and let us know.  </span>
      {
        saveInfos.map(si => {
          // console.log('showing saveinfo ', si)

          const agoStr = timeAgo.format(new Date(si.timestamp))

          const doRestore = () => {
            serverAPI.callPluginMethod("do_restore", {
              save_info: si
            }).then(() => {
              serverAPI.toaster.toast({
                title: 'Steamback',
                body: `Reverted ${si.game_info.game_name} from snapshot`,
                icon: <FiUpload />,
              })
            }).catch(error =>
              console.error('Steamback restore', error)
            )
          }

          // raise a modal dialog to confirm the user wants to restore
          const askRestore = () => {
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
          const descText = si.is_undo ? `Reverts recent Stemback changes` : `Snapshot from ${agoStr}`
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

  const supportedHtml = supportedGameInfos.length < 1 ?
    <span style={{ padding: '1rem', display: 'block' }}>Unfortunately, none of the currently installed games are supported.  Please check for new steamback versions occasionally...</span> :
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

      {snapshotHtml}

      <PanelSection title="Supported games">
        {supportedHtml}
      </PanelSection>
    </div>
  )
}



export default definePlugin((serverApi: ServerAPI) => {

  TimeAgo.addDefaultLocale(en)

  const taskHook = SteamClient.GameSessions.RegisterForAppLifetimeNotifications(async (n: LifetimeNotification) => {
    // console.log("Steamback AppLifetimeNotification", n);

    if (!n.bRunning) {
      try {
        const gameInfo: GameInfo = await makeGameInfo(n.unAppID)
        console.log("Steamback backup game: ", gameInfo)
        const r = await serverApi.callPluginMethod("do_backup", {
          game_info: gameInfo
        })

        const saveinfo = r.result as SaveInfo
        console.log("steamback backup results", saveinfo)
        if (saveinfo)
          serverApi.toaster.toast({
            title: 'Steamback',
            body: `${gameInfo.game_name} snapshot taken`,
            icon: <FiDownload />,
          });
      }
      catch (error: any) {
        console.error('Steamback backup', error)
      }
    }
  })

  let sid = new SteamID(App.m_CurrentUser.strSteamID)

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
