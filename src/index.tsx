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
  LifetimeNotification
} from "decky-frontend-lib";
import { VFC, useState, useRef, useEffect } from "react";
import { FiDownload, FiUpload } from "react-icons/fi";
import SteamID from "steamid";
import TimeAgo from "javascript-time-ago"
import en from "javascript-time-ago/locale/en"

// import logo from "../assets/logo.png";

declare let App: any

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
        <PanelSectionRow>
          <ButtonItem
            layout="below">
            Server says yolo
          </ButtonItem>
        </PanelSectionRow>

        {
          saveInfos.map(si => {
            console.log('showing saveinfo ', si);
            return <PanelSectionRow>
              <ButtonItem
                layout="below">
                SI { si.game_id }: { timeAgo.format(new Date(si.timestamp)) }
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
        const saveinfo = r.result
        console.log("deckshot backup results", saveinfo)
        if (saveinfo)
          serverApi.toaster.toast({
            title: 'Deckshot',
            body: 'Save game snapshot taken',
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
