/*********************************************************************
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2019, Bielefeld University
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of Bielefeld University nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 *********************************************************************/

/* Authors: Robert Haschke
   Desc:    Generator Stage to place an object at a certain pose
*/

#pragma once

#include <moveit/task_constructor/stages/generate_pose.h>
namespace moveit {
namespace task_constructor {
namespace stages {

/** Simple IK pose generator to place an attached object in a specific pose
 *
 * The "pose" property, inherited from GeneratePose specifies the target pose
 * of the grasped object. This stage transforms this pose into a target pose for the ik_frame */
class GenerateSurfacePlace : public GeneratePose
{
public:
	GenerateSurfacePlace(const std::string& name = "place pose");

	void compute() override;

	void setObject(const std::string& object) { setProperty("object", object); }
	void setHandFrame(const std::string& frame) { setProperty("hand_frame", frame); }
	void setSurface(const std::string& surface) { setProperty("surface", surface); }
	void setPlaceOrientation(const Eigen::Quaterniond& orientation) { setProperty("place_orientation", orientation); }
	void setSampleStep(double step) { setProperty("sample_step", step); }

protected:
	void onNewSolution(const SolutionBase& s) override;

};
}  // namespace stages
}  // namespace task_constructor
}  // namespace moveit
