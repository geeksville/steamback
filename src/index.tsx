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
} from "decky-frontend-lib";
import { VFC, useState, useRef, useEffect } from "react";
import { FiDownload, FiUpload } from "react-icons/fi";
import SteamID from "steamid";
import TimeAgo from "javascript-time-ago"
import en from "javascript-time-ago/locale/en"


// FIXME - find a better source for these defs?, I'm hand specifying here
// based on looking at ProtonDB plugin
declare let App: any // used for m_currentUser

declare namespace appStore {
  function GetAppOverviewByGameID(appId: number): AppOverview
}

interface SaveInfo {
  game_id: number;
  timestamp: number;
  filename: string;
  is_undo: boolean
}


const DeckshotContent: VFC<{ serverAPI: ServerAPI }> = ({ serverAPI }) => {
  const [saveInfos, setSaveInfos] = useState<SaveInfo[]>([]);
  const [supportedGameIds, setSupportedGameIds] = useState<number[]>([]);

  // Create formatter (English).
  const timeAgo = new TimeAgo('en-US')

  // Find which games we can work on
  async function getSupported() {
    const folders = await SteamClient.InstallFolder.GetInstallFolders()
    let appIds: number[] = []
    for (let f of folders) {
      for (let a of f.vecApps) {
        appIds = appIds.concat(a.nAppID)
      }
    }
    // console.log("installed apps", appIds)
    const r = await serverAPI.callPluginMethod("find_supported", {
      game_ids: appIds
    })

    // console.log("deckshot supported", r.result)
    setSupportedGameIds(r.result as number[])
  }

  useEffect(() => {
    getSupported()

    serverAPI.callPluginMethod("get_saveinfos", {}).then(saveinfo => {
      // console.log("deckshot saveinfos", saveinfo.result)
      setSaveInfos(saveinfo.result as SaveInfo[])
    }).catch(e => {
      console.error("deckshot saveinfos failed", e)
    })
  }, []) // extra [] at end means only run for first render

  /// Only show snapshot section if we have some saveinfos
  const snapshotHtml = saveInfos.length < 1 ?
    <div></div> :
    <PanelSection title="Snapshots">
      <span style={{ padding: '1rem', display: 'block' }}>This plugin is currently in <b>alpha</b> testing, if you see problems use the 'Undo' button and let us know.  </span>
      {
        saveInfos.map(si => {
          // console.log('showing saveinfo ', si);

          const appDetails = appStore.GetAppOverviewByGameID(si.game_id)
          const agoStr = timeAgo.format(new Date(si.timestamp))

          const doRestore = () => {
            serverAPI.callPluginMethod("do_restore", {
              save_info: si
            }).then(() => {
              serverAPI.toaster.toast({
                title: 'Deckshot',
                body: `Reverted ${appDetails.display_name} from snapshot`,
                icon: <FiUpload />,
              });
            }).catch(error =>
              console.error('Deckshot restore', error)
            )
          }

          // raise a modal dialog to confirm the user wants to restore
          const askRestore = () => {
            const title = si.is_undo ? "Revert recent snapshot" : "Revert to snapshot"
            const message = si.is_undo ?
              `Are you sure you want to undo your changes to ${appDetails.display_name}?` :
              `Are you sure you want to revert ${appDetails.display_name} to the save from ${agoStr}?`

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
          const buttonText = si.is_undo ? `Undo ${appDetails.display_name} changes` : `${appDetails.display_name} ${agoStr}`
          return <PanelSectionRow>
            <ButtonItem onClick={askRestore}
              disabled={runningApps.has(si.game_id)} // Don't let user restore files while game is running
              layout="below">
              {buttonText}
            </ButtonItem>
          </PanelSectionRow>
        })
      }
    </PanelSection>

  const supportedHtml = supportedGameIds.length < 1 ?
    <span style={{ padding: '1rem', display: 'block' }}>Unfortunately, none of the currently installed games are supported.  Please check for new deckshot versions occasionally...</span> :
    <ul style={{ listStyleType: 'none', padding: '1rem' }}>
      {
        supportedGameIds.map(id => {
          // console.log('showing supported ', id)
          const appDetails = appStore.GetAppOverviewByGameID(id)

          return <li style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', paddingBottom: '10px', width: '100%', justifyContent: 'space-between' }}>
            <span>{appDetails.display_name}</span>
          </li>
        })
      }
    </ul>

  const helpUrl = "https://github.com/geeksville/deckshot/blob/main/README.md"
  return (
    <div>
      <span style={{ padding: '1rem', display: 'block' }}><a href={helpUrl} onClick={async () => {
        Navigation.CloseSideMenus()
        Navigation.NavigateToExternalWeb(
          `${helpUrl}`
        )
      }}>Deckshot</a> automatically takes save-game snapshots for many Steam games. See our github page for more information.</span>

      {snapshotHtml}

      <PanelSection title="Supported games">
        {supportedHtml}
      </PanelSection>
    </div>
  );
};



export default definePlugin((serverApi: ServerAPI) => {

  TimeAgo.addDefaultLocale(en)

  const taskHook = SteamClient.GameSessions.RegisterForAppLifetimeNotifications((n: LifetimeNotification) => {
    // console.log("Deckshot AppLifetimeNotification", n);

    if (!n.bRunning) {
      serverApi.callPluginMethod("do_backup", {
        game_id: n.unAppID
      }).then((r) => {
        const saveinfo = r.result as SaveInfo
        console.log("deckshot backup results", saveinfo)
        if (saveinfo)
          serverApi.toaster.toast({
            title: 'Deckshot',
            body: `${appStore.GetAppOverviewByGameID(saveinfo.game_id).display_name} snapshot taken`,
            icon: <FiDownload />,
          });
      }).catch(error =>
        console.error('Deckshot backup', error)
      )
    }
  })

  let sid = new SteamID(App.m_CurrentUser.strSteamID);

  serverApi.callPluginMethod("set_account_id", {
    id_num: sid.accountid
  }).catch(e =>
      console.error("Can't set deckshot account", e)
    )

  return {
    title: <div className={staticClasses.Title}>Deckshot</div>,
    content: <DeckshotContent serverAPI={serverApi} />,
    icon: <FiDownload />,
    onDismount() {
      taskHook!.unregister();
    },
  };
});
