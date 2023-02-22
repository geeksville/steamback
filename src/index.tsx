import {
  ButtonItem,
  definePlugin,
  DialogButton,
  // Menu, MenuItem, showContextMenu,
  PanelSection,
  PanelSectionRow,
  Router,
  ServerAPI,
  staticClasses,
  SteamClient,
  LifetimeNotification,
  showModal,
  ConfirmModal
} from "decky-frontend-lib";
import { VFC, useState, useRef, useEffect } from "react";
import { FiDownload, FiUpload } from "react-icons/fi";
import SteamID from "steamid";
import TimeAgo from "javascript-time-ago"
import en from "javascript-time-ago/locale/en"

// import logo from "../assets/logo.png";

// FIXME - find a better source for these defs?, I'm hand specifying here
// based on looking at ProtonDB plugin
declare let App: any
type AppOverview = {
  app_type: number
  appid: string
  display_name: string
  // display_status: DisplayStatus
  sort_as: string
}
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
  const ref = useRef(true);

  // Create formatter (English).
  const timeAgo = new TimeAgo('en-US')

  // FIXME nasty hack to check if this is our first render.  Only then do we do our plugin read
  // per https://www.developerupdates.com/blog/how-to-check-if-react-functional-component-first-time-render-using-hooks
  useEffect(() => {
    const firstRender = ref.current;

    if (firstRender) {
      ref.current = false;
      console.log('First Render');

      serverAPI.callPluginMethod("get_saveinfos", {}).then(saveinfo => {
        console.log("deckshot saveinfos", saveinfo.result)
        setSaveInfos(saveinfo.result as SaveInfo[])
      }).catch(e => {
        console.log("deckshot saveinfos failed", e)
      })
    } else {
      console.log('Not a first Render');
    }
  })
  
  return (
    <div>
      <PanelSection title="Settings">
      </PanelSection>
      <PanelSection title="Snapshots">
        {
          saveInfos.map(si => {
            console.log('showing saveinfo ', si);

            const appDetails = appStore.GetAppOverviewByGameID(si.game_id)
            const agoStr = timeAgo.format(new Date(si.timestamp))

            const doRestore = () => {
              serverAPI.callPluginMethod("do_restore", {
                save_info: si
              }).then(() => {
                  serverAPI.toaster.toast({
                    title: 'Deckshot',
                    body: `Reverted ${ appDetails.display_name} from snapshot`,
                    icon: <FiUpload />,
                  });
              }).catch(error =>
                console.error('Deckshot restore', error)
              )
            }

            // raise a modal dialog to confirm the user wants to restore
            const askRestore = () => {
              showModal(
                <ConfirmModal
                  onOK= { doRestore }
                  strTitle="Revert to snapshot"
                  strDescription={`Are you sure you want to revert ${appDetails.display_name} to the save from ${ agoStr }?`}
                />, window
              )
            }

            return <PanelSectionRow>
              <ButtonItem onClick={ askRestore }
                layout="below">
                { appDetails.display_name } { agoStr }
              </ButtonItem>
            </PanelSectionRow>
          })
        }
      </PanelSection>
    </div>          
  );
};

/*
old code

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={(e) =>
            showContextMenu(
              <Menu label="Menu" cancelText="CAAAANCEL" onCancel={() => {}}>
                <MenuItem onSelected={() => {}}>Item #1</MenuItem>
                <MenuItem onSelected={() => {}}>Item #2</MenuItem>
                <MenuItem onSelected={() => {}}>Item #3</MenuItem>
              </Menu>,
              e.currentTarget ?? window
            )
          }
        >
          Server says yolo
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <img src={logo} />
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={() => {
            Router.CloseSideMenus();
            Router.Navigate("/deckshot");
          }}
        >
          Router
        </ButtonItem>
      </PanelSectionRow>
*/

const DeckshotPluginRouter: VFC = () => {
  return (
    <div style={{ marginTop: "50px", color: "white" }}>
      Hello World!
      <DialogButton onClick={() => Router.NavigateToLibraryTab()}>
        Go to Library
      </DialogButton>
    </div>
  );
};

export default definePlugin((serverApi: ServerAPI) => {

  TimeAgo.addDefaultLocale(en)

  serverApi.routerHook.addRoute("/deckshot", DeckshotPluginRouter, {
    exact: true,
  });

  /*
  const startHook = SteamClient.Apps.RegisterForGameActionStart((actionType: number, id: string, action: string) => {
    console.log("Deckshot GameActionStart", actionType, id, action);
    
    Deckshot GameActionStart 1 648800 LaunchApp - when lanched raft

    serverAPI.callPluginMethod<GameActionStartParams, {}>("on_game_start_callback", {
      idk: actionType,
      game_id: id,
      action: action
    }).then(() => updatePlaytimesThrottled(serverAPI)); 
});
  */

  
  // RegisterForGameActionTaskChange doesn't seem useful - similar to GameActionStart
  // RegisterForGameActionUserRequest doesn't seem useful - similar to GameActionStart
  // RegisterForAppOverviewChanges returns nasty binary arrays
  // RegisterForAppDetails not useful
  // RegisterForGameActionShowUI not useful
  // RegisterForGameActionShowError not useful
  // RegisterForWorkshopChanges not useful
  // YAY! Deckshot RegisterForAppLifetimeNotifications {unAppID: 648800, nInstanceID: 28768, bRunning: true} is a
  // LifetimeNotification
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
            body: `${ appStore.GetAppOverviewByGameID(saveinfo.game_id).display_name } snapshot taken`,
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
  }).then((r) =>
    console.log("Python replied", r.result))

  return {
    title: <div className={staticClasses.Title}>Deckshot</div>,
    content: <DeckshotContent serverAPI={serverApi} />,
    icon: <FiDownload />,
    onDismount() {
      taskHook!.unregister();
      serverApi.routerHook.removeRoute("/deckshot");
    },
  };
});
