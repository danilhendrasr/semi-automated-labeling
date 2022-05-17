// Copyright (C) 2021-2022 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import { RouteComponentProps } from 'react-router-dom';
import Input from 'antd/lib/input';
import copy from 'copy-to-clipboard';

import {
    activateObject,
    changeFrameAsync,
    changeWorkspace as changeWorkspaceAction,
    collectStatisticsAsync,
    redoActionAsync,
    saveAnnotationsAsync,
    searchAnnotationsAsync,
    searchEmptyFrameAsync,
    setForceExitAnnotationFlag as setForceExitAnnotationFlagAction,
    switchPredictor as switchPredictorAction,
    getPredictionsAsync,
    showFilters as showFiltersAction,
    showStatistics as showStatisticsAction,
    switchPlay,
    undoActionAsync,
} from 'actions/annotation-actions';
import AnnotationTopBarComponent from 'components/annotation-page/top-bar/top-bar';
import { Canvas } from 'cvat-canvas-wrapper';
import { Canvas3d } from 'cvat-canvas3d-wrapper';
import {
    CombinedState,
    FrameSpeed,
    Workspace,
    PredictorState,
    DimensionType,
    ActiveControl,
    ToolsBlockerState,
} from 'reducers/interfaces';
import isAbleToChangeFrame from 'utils/is-able-to-change-frame';
import GlobalHotKeys, { KeyMap } from 'utils/mousetrap-react';
import { switchToolsBlockerState } from 'actions/settings-actions';

interface StateToProps {
    jobInstance: any;
    frameNumber: number;
    frameFilename: string;
    frameStep: number;
    frameSpeed: FrameSpeed;
    frameDelay: number;
    frameFetching: boolean;
    playing: boolean;
    saving: boolean;
    canvasIsReady: boolean;
    savingStatuses: string[];
    undoAction?: string;
    redoAction?: string;
    autoSave: boolean;
    autoSaveInterval: number;
    toolsBlockerState: ToolsBlockerState;
    workspace: Workspace;
    keyMap: KeyMap;
    normalizedKeyMap: Record<string, string>;
    canvasInstance: Canvas | Canvas3d;
    forceExit: boolean;
    predictor: PredictorState;
    activeControl: ActiveControl;
    isTrainingActive: boolean;
}

interface DispatchToProps {
    onChangeFrame(frame: number, fillBuffer?: boolean, frameStep?: number): void;
    onSwitchPlay(playing: boolean): void;
    onSaveAnnotation(sessionInstance: any): void;
    showStatistics(sessionInstance: any): void;
    showFilters(sessionInstance: any): void;
    undo(sessionInstance: any, frameNumber: any): void;
    redo(sessionInstance: any, frameNumber: any): void;
    searchAnnotations(sessionInstance: any, frameFrom: number, frameTo: number): void;
    searchEmptyFrame(sessionInstance: any, frameFrom: number, frameTo: number): void;
    setForceExitAnnotationFlag(forceExit: boolean): void;
    changeWorkspace(workspace: Workspace): void;
    switchPredictor(predictorEnabled: boolean): void;
    onSwitchToolsBlockerState(toolsBlockerState: ToolsBlockerState): void;
}

function mapStateToProps(state: CombinedState): StateToProps {
    const {
        annotation: {
            player: {
                playing,
                frame: {
                    filename: frameFilename, number: frameNumber, delay: frameDelay, fetching: frameFetching,
                },
            },
            annotations: {
                saving: { uploading: saving, statuses: savingStatuses, forceExit },
                history,
            },
            job: { instance: jobInstance },
            canvas: { ready: canvasIsReady, instance: canvasInstance, activeControl },
            workspace,
            predictor,
        },
        settings: {
            player: { frameSpeed, frameStep },
            workspace: { autoSave, autoSaveInterval, toolsBlockerState },
        },
        shortcuts: { keyMap, normalizedKeyMap },
        plugins: { list },
    } = state;

    return {
        frameStep,
        frameSpeed,
        frameDelay,
        frameFetching,
        playing,
        canvasIsReady,
        saving,
        savingStatuses,
        frameNumber,
        frameFilename,
        jobInstance,
        undoAction: history.undo.length ? history.undo[history.undo.length - 1][0] : undefined,
        redoAction: history.redo.length ? history.redo[history.redo.length - 1][0] : undefined,
        autoSave,
        autoSaveInterval,
        toolsBlockerState,
        workspace,
        keyMap,
        normalizedKeyMap,
        canvasInstance,
        forceExit,
        predictor,
        activeControl,
        isTrainingActive: list.PREDICT,
    };
}

function mapDispatchToProps(dispatch: any): DispatchToProps {
    return {
        onChangeFrame(frame: number, fillBuffer?: boolean, frameStep?: number): void {
            dispatch(changeFrameAsync(frame, fillBuffer, frameStep));
        },
        onSwitchPlay(playing: boolean): void {
            dispatch(switchPlay(playing));
        },
        onSaveAnnotation(sessionInstance: any): void {
            dispatch(saveAnnotationsAsync(sessionInstance));
        },
        showStatistics(sessionInstance: any): void {
            dispatch(collectStatisticsAsync(sessionInstance));
            dispatch(showStatisticsAction(true));
        },
        showFilters(): void {
            dispatch(showFiltersAction(true));
        },
        undo(sessionInstance: any, frameNumber: any): void {
            dispatch(undoActionAsync(sessionInstance, frameNumber));
        },
        redo(sessionInstance: any, frameNumber: any): void {
            dispatch(redoActionAsync(sessionInstance, frameNumber));
        },
        searchAnnotations(sessionInstance: any, frameFrom: number, frameTo: number): void {
            dispatch(searchAnnotationsAsync(sessionInstance, frameFrom, frameTo));
        },
        searchEmptyFrame(sessionInstance: any, frameFrom: number, frameTo: number): void {
            dispatch(searchEmptyFrameAsync(sessionInstance, frameFrom, frameTo));
        },
        changeWorkspace(workspace: Workspace): void {
            dispatch(activateObject(null, null));
            dispatch(changeWorkspaceAction(workspace));
        },
        setForceExitAnnotationFlag(forceExit: boolean): void {
            dispatch(setForceExitAnnotationFlagAction(forceExit));
        },
        switchPredictor(predictorEnabled: boolean): void {
            dispatch(switchPredictorAction(predictorEnabled));
            if (predictorEnabled) {
                dispatch(getPredictionsAsync());
            }
        },
        onSwitchToolsBlockerState(toolsBlockerState: ToolsBlockerState): void {
            dispatch(switchToolsBlockerState(toolsBlockerState));
        },
    };
}

interface State {
    prevButtonType: 'regular' | 'filtered' | 'empty';
    nextButtonType: 'regular' | 'filtered' | 'empty';
}

type Props = StateToProps & DispatchToProps & RouteComponentProps;
class AnnotationTopBarContainer extends React.PureComponent<Props, State> {
    private inputFrameRef: React.RefObject<Input>;
    private autoSaveInterval: number | undefined;
    private unblock: any;

    constructor(props: Props) {
        super(props);
        this.inputFrameRef = React.createRef<Input>();
        this.state = {
            prevButtonType: 'regular',
            nextButtonType: 'regular',
        };
    }

    public componentDidMount(): void {
        const {
            autoSaveInterval, history, jobInstance, setForceExitAnnotationFlag,
        } = this.props;
        this.autoSaveInterval = window.setInterval(this.autoSave.bind(this), autoSaveInterval);

        // eslint-disable-next-line @typescript-eslint/no-this-alias
        const self = this;
        this.unblock = history.block((location: any) => {
            const { forceExit } = self.props;
            const { id: jobID, taskId: taskID } = jobInstance;

            if (
                jobInstance.annotations.hasUnsavedChanges() &&
                location.pathname !== `/tasks/${taskID}/jobs/${jobID}` &&
                !forceExit
            ) {
                return 'You have unsaved changes, please confirm leaving this page.';
            }

            if (forceExit) {
                setForceExitAnnotationFlag(false);
            }

            return undefined;
        });

        window.addEventListener('beforeunload', this.beforeUnloadCallback);
    }

    public componentDidUpdate(prevProps: Props): void {
        const { autoSaveInterval } = this.props;

        if (autoSaveInterval !== prevProps.autoSaveInterval) {
            if (this.autoSaveInterval) window.clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = window.setInterval(this.autoSave.bind(this), autoSaveInterval);
        }
        this.play();
    }

    public componentWillUnmount(): void {
        window.clearInterval(this.autoSaveInterval);
        window.removeEventListener('beforeunload', this.beforeUnloadCallback);
        this.unblock();
    }

    private undo = (): void => {
        const { undo, jobInstance, frameNumber } = this.props;

        if (isAbleToChangeFrame()) {
            undo(jobInstance, frameNumber);
        }
    };

    private redo = (): void => {
        const { redo, jobInstance, frameNumber } = this.props;

        if (isAbleToChangeFrame()) {
            redo(jobInstance, frameNumber);
        }
    };

    private showStatistics = (): void => {
        const { jobInstance, showStatistics } = this.props;

        showStatistics(jobInstance);
    };

    private showFilters = (): void => {
        const { jobInstance, showFilters } = this.props;

        showFilters(jobInstance);
    };

    private onSwitchPlay = (): void => {
        const {
            frameNumber, jobInstance, onSwitchPlay, playing,
        } = this.props;

        if (playing) {
            onSwitchPlay(false);
        } else if (frameNumber < jobInstance.stopFrame) {
            onSwitchPlay(true);
        }
    };

    private onFirstFrame = (): void => {
        const {
            frameNumber, jobInstance, playing, onSwitchPlay,
        } = this.props;

        const newFrame = jobInstance.startFrame;
        if (newFrame !== frameNumber) {
            if (playing) {
                onSwitchPlay(false);
            }
            this.changeFrame(newFrame);
        }
    };

    private onBackward = (): void => {
        const {
            frameNumber, frameStep, jobInstance, playing, onSwitchPlay,
        } = this.props;

        const newFrame = Math.max(jobInstance.startFrame, frameNumber - frameStep);
        if (newFrame !== frameNumber) {
            if (playing) {
                onSwitchPlay(false);
            }
            this.changeFrame(newFrame);
        }
    };

    private onPrevFrame = (): void => {
        const { prevButtonType } = this.state;
        const {
            frameNumber, jobInstance, playing, onSwitchPlay,
        } = this.props;
        const { startFrame } = jobInstance;

        const newFrame = Math.max(jobInstance.startFrame, frameNumber - 1);
        if (newFrame !== frameNumber) {
            if (playing) {
                onSwitchPlay(false);
            }

            if (prevButtonType === 'regular') {
                this.changeFrame(newFrame);
            } else if (prevButtonType === 'filtered') {
                this.searchAnnotations(frameNumber - 1, startFrame);
            } else {
                this.searchEmptyFrame(frameNumber - 1, startFrame);
            }
        }
    };

    private onNextFrame = (): void => {
        const { nextButtonType } = this.state;
        const {
            frameNumber, jobInstance, playing, onSwitchPlay,
        } = this.props;
        const { stopFrame } = jobInstance;

        const newFrame = Math.min(jobInstance.stopFrame, frameNumber + 1);
        if (newFrame !== frameNumber) {
            if (playing) {
                onSwitchPlay(false);
            }

            if (nextButtonType === 'regular') {
                this.changeFrame(newFrame);
            } else if (nextButtonType === 'filtered') {
                this.searchAnnotations(frameNumber + 1, stopFrame);
            } else {
                this.searchEmptyFrame(frameNumber + 1, stopFrame);
            }
        }
    };

    private onForward = (): void => {
        const {
            frameNumber, frameStep, jobInstance, playing, onSwitchPlay,
        } = this.props;

        const newFrame = Math.min(jobInstance.stopFrame, frameNumber + frameStep);
        if (newFrame !== frameNumber) {
            if (playing) {
                onSwitchPlay(false);
            }
            this.changeFrame(newFrame);
        }
    };

    private onLastFrame = (): void => {
        const {
            frameNumber, jobInstance, playing, onSwitchPlay,
        } = this.props;

        const newFrame = jobInstance.stopFrame;
        if (newFrame !== frameNumber) {
            if (playing) {
                onSwitchPlay(false);
            }
            this.changeFrame(newFrame);
        }
    };

    private onSetPreviousButtonType = (type: 'regular' | 'filtered' | 'empty'): void => {
        this.setState({
            prevButtonType: type,
        });
    };

    private onSetNextButtonType = (type: 'regular' | 'filtered' | 'empty'): void => {
        this.setState({
            nextButtonType: type,
        });
    };

    private onSaveAnnotation = (): void => {
        const { onSaveAnnotation, jobInstance } = this.props;
        onSaveAnnotation(jobInstance);
    };

    private onChangePlayerSliderValue = (value: number): void => {
        const { playing, onSwitchPlay } = this.props;
        if (playing) {
            onSwitchPlay(false);
        }
        this.changeFrame(value as number);
    };

    private onChangePlayerInputValue = (value: number): void => {
        const { onSwitchPlay, playing, frameNumber } = this.props;
        if (value !== frameNumber) {
            if (playing) {
                onSwitchPlay(false);
            }
            this.changeFrame(value);
        }
    };

    private onFinishDraw = (): void => {
        const { activeControl, canvasInstance } = this.props;
        if (
            [ActiveControl.AI_TOOLS, ActiveControl.OPENCV_TOOLS].includes(activeControl) &&
            canvasInstance instanceof Canvas
        ) {
            canvasInstance.interact({ enabled: false });
            return;
        }

        canvasInstance.draw({ enabled: false });
    };

    private onSwitchToolsBlockerState = (): void => {
        const {
            toolsBlockerState, onSwitchToolsBlockerState, canvasInstance, activeControl,
        } = this.props;
        if (canvasInstance instanceof Canvas) {
            if (activeControl.includes(ActiveControl.OPENCV_TOOLS)) {
                canvasInstance.interact({
                    enabled: true,
                    crosshair: toolsBlockerState.algorithmsLocked,
                    enableThreshold: toolsBlockerState.algorithmsLocked,
                });
            }
        }
        onSwitchToolsBlockerState({ algorithmsLocked: !toolsBlockerState.algorithmsLocked });
    };

    private onURLIconClick = (): void => {
        const { frameNumber } = this.props;
        const { origin, pathname } = window.location;
        const url = `${origin}${pathname}?frame=${frameNumber}`;
        copy(url);
    };

    private beforeUnloadCallback = (event: BeforeUnloadEvent): string | undefined => {
        const { jobInstance, forceExit, setForceExitAnnotationFlag } = this.props;
        if (jobInstance.annotations.hasUnsavedChanges() && !forceExit) {
            const confirmationMessage = 'You have unsaved changes, please confirm leaving this page.';
            // eslint-disable-next-line no-param-reassign
            event.returnValue = confirmationMessage;
            return confirmationMessage;
        }

        if (forceExit) {
            setForceExitAnnotationFlag(false);
        }
        return undefined;
    };

    private play(): void {
        const {
            jobInstance,
            frameSpeed,
            frameNumber,
            frameDelay,
            frameFetching,
            playing,
            canvasIsReady,
            onSwitchPlay,
            onChangeFrame,
        } = this.props;

        if (playing && canvasIsReady && !frameFetching) {
            if (frameNumber < jobInstance.stopFrame) {
                let framesSkipped = 0;
                if (frameSpeed === FrameSpeed.Fast && frameNumber + 1 < jobInstance.stopFrame) {
                    framesSkipped = 1;
                }
                if (frameSpeed === FrameSpeed.Fastest && frameNumber + 2 < jobInstance.stopFrame) {
                    framesSkipped = 2;
                }

                setTimeout(() => {
                    const { playing: stillPlaying } = this.props;
                    if (stillPlaying) {
                        if (isAbleToChangeFrame()) {
                            onChangeFrame(frameNumber + 1 + framesSkipped, stillPlaying, framesSkipped + 1);
                        } else if (jobInstance.dimension === DimensionType.DIM_2D) {
                            onSwitchPlay(false);
                        } else {
                            setTimeout(() => this.play(), frameDelay);
                        }
                    }
                }, frameDelay);
            } else {
                onSwitchPlay(false);
            }
        }
    }

    private autoSave(): void {
        const { autoSave, saving } = this.props;

        if (autoSave && !saving) {
            this.onSaveAnnotation();
        }
    }

    private changeFrame(frame: number): void {
        const { onChangeFrame } = this.props;
        if (isAbleToChangeFrame()) {
            onChangeFrame(frame);
        }
    }

    private searchAnnotations(start: number, stop: number): void {
        const { jobInstance, searchAnnotations } = this.props;
        if (isAbleToChangeFrame()) {
            searchAnnotations(jobInstance, start, stop);
        }
    }

    private searchEmptyFrame(start: number, stop: number): void {
        const { jobInstance, searchEmptyFrame } = this.props;
        if (isAbleToChangeFrame()) {
            searchEmptyFrame(jobInstance, start, stop);
        }
    }

    public render(): JSX.Element {
        const { nextButtonType, prevButtonType } = this.state;
        const {
            playing,
            saving,
            savingStatuses,
            jobInstance,
            jobInstance: { startFrame, stopFrame },
            frameNumber,
            frameFilename,
            undoAction,
            redoAction,
            workspace,
            canvasIsReady,
            keyMap,
            normalizedKeyMap,
            predictor,
            isTrainingActive,
            activeControl,
            searchAnnotations,
            changeWorkspace,
            switchPredictor,
            toolsBlockerState,
        } = this.props;

        const preventDefault = (event: KeyboardEvent | undefined): void => {
            if (event) {
                event.preventDefault();
            }
        };

        const subKeyMap = {
            SAVE_JOB: keyMap.SAVE_JOB,
            UNDO: keyMap.UNDO,
            REDO: keyMap.REDO,
            NEXT_FRAME: keyMap.NEXT_FRAME,
            PREV_FRAME: keyMap.PREV_FRAME,
            FORWARD_FRAME: keyMap.FORWARD_FRAME,
            BACKWARD_FRAME: keyMap.BACKWARD_FRAME,
            SEARCH_FORWARD: keyMap.SEARCH_FORWARD,
            SEARCH_BACKWARD: keyMap.SEARCH_BACKWARD,
            PLAY_PAUSE: keyMap.PLAY_PAUSE,
            FOCUS_INPUT_FRAME: keyMap.FOCUS_INPUT_FRAME,
        };

        const handlers = {
            UNDO: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (undoAction) {
                    this.undo();
                }
            },
            REDO: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (redoAction) {
                    this.redo();
                }
            },
            SAVE_JOB: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (!saving) {
                    this.onSaveAnnotation();
                }
            },
            NEXT_FRAME: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (canvasIsReady) {
                    this.onNextFrame();
                }
            },
            PREV_FRAME: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (canvasIsReady) {
                    this.onPrevFrame();
                }
            },
            FORWARD_FRAME: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (canvasIsReady) {
                    this.onForward();
                }
            },
            BACKWARD_FRAME: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (canvasIsReady) {
                    this.onBackward();
                }
            },
            SEARCH_FORWARD: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (frameNumber + 1 <= stopFrame && canvasIsReady && isAbleToChangeFrame()) {
                    searchAnnotations(jobInstance, frameNumber + 1, stopFrame);
                }
            },
            SEARCH_BACKWARD: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (frameNumber - 1 >= startFrame && canvasIsReady && isAbleToChangeFrame()) {
                    searchAnnotations(jobInstance, frameNumber - 1, startFrame);
                }
            },
            PLAY_PAUSE: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                this.onSwitchPlay();
            },
            FOCUS_INPUT_FRAME: (event: KeyboardEvent | undefined) => {
                preventDefault(event);
                if (this.inputFrameRef.current) {
                    this.inputFrameRef.current.focus();
                }
            },
        };

        return (
            <>
                <GlobalHotKeys keyMap={subKeyMap} handlers={handlers} />
                <AnnotationTopBarComponent
                    showStatistics={this.showStatistics}
                    showFilters={this.showFilters}
                    onSwitchPlay={this.onSwitchPlay}
                    onSaveAnnotation={this.onSaveAnnotation}
                    onPrevFrame={this.onPrevFrame}
                    onNextFrame={this.onNextFrame}
                    onForward={this.onForward}
                    onBackward={this.onBackward}
                    onFirstFrame={this.onFirstFrame}
                    onLastFrame={this.onLastFrame}
                    setNextButtonType={this.onSetNextButtonType}
                    setPrevButtonType={this.onSetPreviousButtonType}
                    onSliderChange={this.onChangePlayerSliderValue}
                    onInputChange={this.onChangePlayerInputValue}
                    onURLIconClick={this.onURLIconClick}
                    changeWorkspace={changeWorkspace}
                    switchPredictor={switchPredictor}
                    predictor={predictor}
                    workspace={workspace}
                    playing={playing}
                    saving={saving}
                    savingStatuses={savingStatuses}
                    startFrame={startFrame}
                    stopFrame={stopFrame}
                    frameNumber={frameNumber}
                    frameFilename={frameFilename}
                    inputFrameRef={this.inputFrameRef}
                    undoAction={undoAction}
                    redoAction={redoAction}
                    saveShortcut={normalizedKeyMap.SAVE_JOB}
                    undoShortcut={normalizedKeyMap.UNDO}
                    redoShortcut={normalizedKeyMap.REDO}
                    drawShortcut={normalizedKeyMap.SWITCH_DRAW_MODE}
                    // this shortcut is handled in interactionHandler.ts separatelly
                    switchToolsBlockerShortcut={normalizedKeyMap.SWITCH_TOOLS_BLOCKER_STATE}
                    playPauseShortcut={normalizedKeyMap.PLAY_PAUSE}
                    nextFrameShortcut={normalizedKeyMap.NEXT_FRAME}
                    previousFrameShortcut={normalizedKeyMap.PREV_FRAME}
                    forwardShortcut={normalizedKeyMap.FORWARD_FRAME}
                    backwardShortcut={normalizedKeyMap.BACKWARD_FRAME}
                    nextButtonType={nextButtonType}
                    prevButtonType={prevButtonType}
                    focusFrameInputShortcut={normalizedKeyMap.FOCUS_INPUT_FRAME}
                    onUndoClick={this.undo}
                    onRedoClick={this.redo}
                    onFinishDraw={this.onFinishDraw}
                    onSwitchToolsBlockerState={this.onSwitchToolsBlockerState}
                    toolsBlockerState={toolsBlockerState}
                    jobInstance={jobInstance}
                    isTrainingActive={isTrainingActive}
                    activeControl={activeControl}
                />
            </>
        );
    }
}

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(AnnotationTopBarContainer));
