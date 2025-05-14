import { Badge, Card, Col, ListGroup, CloseButton, Button, ProgressBar } from "react-bootstrap";
import React, { useEffect, useState } from 'react';
import { getToken } from "../App"
import axios from 'axios';

function Post({ post, removePost, updatePost }) {
    const [showCard, setShowCard] = useState(true);
    const [attachment, setAttachment] = useState(null);
    const [image, setImage] = useState(null);
    const [labeling, setLabeling] = useState(null)

    const fileChanged = (e) => {
        const files = e.target.files || e.dataTransfer.files;
        if (!files.length) return;
        console.log(files[0]);
        setAttachment(files[0]);
    }
    const getSignedUrlPut = async (postId) => {
        console.log("Getting signed URL");
        console.log(attachment.name)
        const config = {
            headers: { Authorization: getToken() },
            params: {
                filename: attachment.name,
                filetype: attachment.type,
                postId: postId,
            },
        };

        const response = await axios.get("/signedUrlPut", config);
        return new URL(response.data.uploadURL);
    }
    const submitFile = async () => {
        if (!attachment) {
            alert("Please select a file to upload.");
        }
        const postId = post.id.split("#")[1];
        const uploadUrl = await getSignedUrlPut(postId);

        const config = {
            headers: { "Content-Type": attachment.type },
        };
        console.log(`Uploading to S3: ${uploadUrl}`);

        var instance = axios.create();
        delete instance.defaults.headers.common['Authorization'];
        setLabeling(true)

        const res = await instance.put(uploadUrl, attachment, config)
        setTimeout(() => {
            console.log(res.status); // HTTP status
            setLabeling(false)
            updatePost()
          }, 2000);
    }

    const deletePost = async () => {
        const id = post.id;
        console.log(`/posts/${post.id}`)
        axios.delete(`/posts/${id}`, { headers: { Authorization: getToken() } })
            .then(res => {
                console.log(post.id);
                setShowCard(false);
            })
            .catch((error) =>{
                console.log('Error', error.message);
                });;

    };

    return (<>
        {showCard && (
            <Col>
                <Card style={{ marginTop: '1rem', }} key={post.id}>
                    <Card.Header >{post.title} <CloseButton className="float-end" onClick={deletePost} /></Card.Header>
                    <Card.Img variant="top" src={post.image} />
                    <Card.Body>
                        <Card.Text>
                            {post.body}
                        </Card.Text>
                    </Card.Body>
                    <ListGroup variant="flush">
                        {post.labels
                            ?
                            <ListGroup.Item>

                                {post.labels.map((label) => (
                                    <Badge key={label} bg="info">
                                        {label}
                                    </Badge>
                                ))}{' '}
                            </ListGroup.Item>
        
                            : 
                            <ListGroup.Item>
                                Attachment:
                                <input type="file" onChange={fileChanged} />
                                <Button
                                    variant="primary"
                                    onClick={submitFile}
                                >
                                    Upload
                                </Button>
                                {labeling &&
                                <ProgressLabeling/>
                                }
                            </ListGroup.Item>
                            }
                    </ListGroup>
                </Card>
            </Col>
        )}
    </>
    )
}

function ProgressLabeling() {
    const [progress, setProgress] = useState(0);
  
    useEffect(() => {
      const timer = setInterval(() => {
        if (progress < 100) {
          setProgress(progress + 1);
        }
      }, 10);
  
      return () => {
        clearInterval(timer);
      };
    }, [progress]);
  
    return (
      <div className="App">
        <ProgressBar now={progress} label="Detecting labels" />
      </div>
    );
  }
  


export default Post