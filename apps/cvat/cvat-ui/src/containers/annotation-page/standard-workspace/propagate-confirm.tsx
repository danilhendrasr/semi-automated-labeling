// Copyright (C) 2020-2021 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { connect } from 'react-redux';

import {
    propagateObject as propagateObjectAction,
    changePropagateFrames as changePropagateFramesAction,
    propagateObjectAsync,
} from 'actions/annotation-actions';

import { CombinedState } from 'reducers/interfaces';
import PropagateConfirmComponent from 'components/annotation-page/standard-workspace/propagate-confirm';

interface StateToProps {
    objectState: any | null;
    frameNumber: number;
    stopFrame: number;
    propagateFrames: number;
    jobInstance: any;
}

interface DispatchToProps {
    cancel(): void;
    propagateObject(sessionInstance: any, objectState: any, from: number, to: number): void;
    changePropagateFrames(frames: number): void;
}

function mapStateToProps(state: CombinedState): StateToProps {
    const {
        annotation: {
            propagate: { objectState, frames: propagateFrames },
            job: {
                instance: { stopFrame },
                instance: jobInstance,
            },
            player: {
                frame: { number: frameNumber },
            },
        },
    } = state;

    return {
        objectState,
        frameNumber,
        stopFrame,
        propagateFrames,
        jobInstance,
    };
}

function mapDispatchToProps(dispatch: any): DispatchToProps {
    return {
        propagateObject(sessionInstance: any, objectState: any, from: number, to: number): void {
            dispatch(propagateObjectAsync(sessionInstance, objectState, from, to));
        },
        changePropagateFrames(frames: number): void {
            dispatch(changePropagateFramesAction(frames));
        },
        cancel(): void {
            dispatch(propagateObjectAction(null));
        },
    };
}

type Props = StateToProps & DispatchToProps;
class PropagateConfirmContainer extends React.PureComponent<Props> {
    private propagateObject = (): void => {
        const {
            propagateObject, objectState, propagateFrames, frameNumber, stopFrame, jobInstance,
        } = this.props;

        const propagateUpToFrame = Math.min(frameNumber + propagateFrames, stopFrame);
        propagateObject(jobInstance, objectState, frameNumber + 1, propagateUpToFrame);
    };

    private changePropagateFrames = (value: number): void => {
        const { changePropagateFrames } = this.props;
        changePropagateFrames(value);
    };

    private changeUpToFrame = (value: number): void => {
        const { stopFrame, frameNumber, changePropagateFrames } = this.props;

        const propagateFrames = Math.max(0, Math.min(stopFrame, value)) - frameNumber;
        changePropagateFrames(propagateFrames);
    };

    public render(): JSX.Element {
        const {
            frameNumber, stopFrame, propagateFrames, cancel, objectState,
        } = this.props;

        const propagateUpToFrame = Math.min(frameNumber + propagateFrames, stopFrame);

        return (
            <PropagateConfirmComponent
                visible={objectState !== null}
                propagateUpToFrame={propagateUpToFrame}
                stopFrame={stopFrame}
                frameNumber={frameNumber}
                propagateFrames={propagateUpToFrame - frameNumber}
                propagateObject={this.propagateObject}
                changePropagateFrames={this.changePropagateFrames}
                changeUpToFrame={this.changeUpToFrame}
                cancel={cancel}
            />
        );
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(PropagateConfirmContainer);
